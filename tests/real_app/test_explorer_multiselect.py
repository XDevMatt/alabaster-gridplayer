"""Files and a folder picked together in Explorer, opened with the player:
Explorer starts one player for each, all at once. They end in one window,
a cell for each file and one cell playing the folder as a list.

Each player runs as a user starts it (python -m gridplayer <item>), with
data and settings of its own, and writes down what its window has.
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.real_app,
    pytest.mark.skipif(not sys.platform.startswith("linux"), reason="X11"),
    pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="needs an X display"),
    pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg"),
]

REPO = Path(__file__).resolve().parents[2]
FILES = 12
SETTLED_WITHIN_S = 45.0

SETTLE_SCRIPT = (
    "import sys\n"
    "from gridplayer.params.static import AddMode, UnsavedChangesMode\n"
    "from gridplayer.settings import Settings\n"
    "s = Settings()\n"
    "s.set('playlist/unsaved_changes', UnsavedChangesMode.DISCARD)\n"
    "if sys.argv[1] != 'default':\n"
    "    s.set('playlist/add_mode', AddMode(sys.argv[1]))\n"
    "s.settings.sync()\n"
)

# the player, writing down every so often what each cell of its window plays
REPORTING_PLAYER = """
import json, os, sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

out = os.environ["GP_TEST_REPORT_DIR"]
exec_ = QApplication.exec_

def report():
    for widget in QApplication.topLevelWidgets():
        if type(widget).__name__ != "Player" or not widget.isVisible():
            continue
        cells = []
        for block in widget._context.video_blocks:
            media_list = block.media_list
            cells.append({
                "uri": str(block.video_params.uri) if block.video_params else None,
                "list": [str(i.uri) for i in media_list.items] if media_list else None,
            })
        tmp = f"{out}/{os.getpid()}.tmp"
        with open(tmp, "w") as f:
            json.dump(cells, f)
        os.replace(tmp, f"{out}/{os.getpid()}.json")

def reporting_exec_(self):
    self._report_timer = QTimer()
    self._report_timer.timeout.connect(report)
    self._report_timer.start(250)
    return exec_()

QApplication.exec_ = reporting_exec_
sys.argv = ["gridplayer", *sys.argv[1:]]
from gridplayer.__main__ import main
main()
"""


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    root = tmp_path_factory.mktemp("picked")
    clip = root / "clip.mp4"
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:duration=20",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
         str(clip)],
        check=True,
    )  # fmt: skip

    files = []
    for i in range(1, FILES + 1):
        path = root / f"video {i:02}.mp4"
        shutil.copy(clip, path)
        files.append(path)

    folder = root / "Shows"
    folder.mkdir()
    shows = []
    for i in range(1, 4):
        path = folder / f"episode {i}.mp4"
        shutil.copy(clip, path)
        shows.append(path)

    return files, folder, shows


@pytest.fixture
def home():
    # short: the instance socket's path has to fit in about 100 bytes
    where = Path(tempfile.mkdtemp(prefix="gp-ms-"))
    (where / "rt").mkdir(mode=0o700)
    (where / "report").mkdir()
    yield where
    shutil.rmtree(where, ignore_errors=True)


def _env(home: Path) -> dict:
    return {
        **os.environ,
        "GP_USER_DATA_DIR": str(home / "data"),
        "XDG_DATA_HOME": str(home / "data"),
        "XDG_CONFIG_HOME": str(home / "config"),
        "XDG_CACHE_HOME": str(home / "cache"),
        "XDG_RUNTIME_DIR": str(home / "rt"),
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/nonexistent/gridplayer-ms",
        "QT_QPA_PLATFORM": "xcb",
        "GP_TEST_REPORT_DIR": str(home / "report"),
        "PYTHONPATH": str(REPO),
    }


def _open_all_at_once(home, items, add_mode):
    env = _env(home)
    subprocess.run(
        [sys.executable, "-c", SETTLE_SCRIPT, add_mode], cwd=REPO, env=env, check=True
    )

    return [
        subprocess.Popen(
            [sys.executable, "-c", REPORTING_PLAYER, str(item)],
            cwd=REPO,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for item in items
    ]


def _windows(home, players, cells_expected):
    """What each player still running has in its window, once they all
    have what was opened, or as they are at the deadline."""

    deadline = time.monotonic() + SETTLED_WITHIN_S

    while True:
        running = {p.pid for p in players if p.poll() is None}
        windows = {
            int(f.stem): json.loads(f.read_text())
            for f in (home / "report").glob("*.json")
            if int(f.stem) in running
        }
        placed = sum(len(cells) for cells in windows.values())

        if placed >= cells_expected or time.monotonic() > deadline:
            # a moment for anything else that was on its way
            time.sleep(1)
            running = {p.pid for p in players if p.poll() is None}
            return {
                pid: json.loads((home / "report" / f"{pid}.json").read_text())
                for pid in running
                if (home / "report" / f"{pid}.json").exists()
            }, running

        time.sleep(0.25)


def _close(players):
    for player in players:
        if player.poll() is None:
            os.killpg(player.pid, signal.SIGKILL)
        player.wait(timeout=10)


@pytest.mark.parametrize("add_mode", ["default", "one_cell"])
def test_one_window_a_cell_a_file_one_for_the_folder(home, media, add_mode):
    files, folder, shows = media
    items = [*files, folder]

    players = _open_all_at_once(home, items, add_mode)
    try:
        windows, running = _windows(home, players, len(items))
    finally:
        _close(players)

    assert len(running) == 1, f"{len(running)} players left running"
    assert len(windows) == 1, f"{len(windows)} windows"

    (cells,) = windows.values()
    singles = sorted(cell["uri"] for cell in cells if cell["list"] is None)
    lists = [cell["list"] for cell in cells if cell["list"] is not None]

    assert singles == sorted(map(str, files))
    assert lists == [list(map(str, shows))]
