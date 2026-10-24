"""Closing the window ends the app: the process and every process it
started are gone within seconds, with nothing left running windowless.

The app runs as a user starts it (python -m gridplayer <video>), on the X
display xvfb gives the test, with data and settings of its own. The window
is closed the way a window manager closes it, with WM_DELETE_WINDOW.
"""

import ctypes
import ctypes.util
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.real_app,
    pytest.mark.skipif(not sys.platform.startswith("linux"), reason="X11 and /proc"),
    pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="needs an X display"),
    pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg"),
    pytest.mark.skipif(shutil.which("xdotool") is None, reason="needs xdotool"),
    pytest.mark.skipif(ctypes.util.find_library("X11") is None, reason="needs libX11"),
]

REPO = Path(__file__).resolve().parents[2]
# well inside the exit watchdog's 10 s: an exit here is the ordinary one
GONE_WITHIN_S = 6.0
OPEN_WITHIN_S = 30.0

SETTLE_SCRIPT = (
    "from gridplayer.params.static import UnsavedChangesMode\n"
    "from gridplayer.settings import Settings\n"
    "s = Settings()\n"
    "s.set('playlist/unsaved_changes', UnsavedChangesMode.DISCARD)\n"
    "s.settings.sync()\n"
)


@pytest.fixture(scope="module")
def clip(tmp_path_factory):
    path = tmp_path_factory.mktemp("clip") / "clip.mp4"
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "testsrc=size=320x180:rate=25:duration=30",
         "-f", "lavfi", "-i", "sine=d=30",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-shortest", str(path)],
        check=True,
    )  # fmt: skip
    return path


@pytest.fixture
def home():
    # short: the instance socket's path has to fit in about 100 bytes
    where = Path(tempfile.mkdtemp(prefix="gp-exit-"))
    (where / "rt").mkdir(mode=0o700)
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
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/nonexistent/gridplayer-exit",
        "QT_QPA_PLATFORM": "xcb",
    }


def _settle(home: Path):
    """Settings of the app's own: no question about saving on the way out."""

    subprocess.run(
        [sys.executable, "-c", SETTLE_SCRIPT],
        cwd=REPO,
        env=_env(home),
        check=True,
        timeout=60,
    )


def _descendants(pid: int) -> set[int]:
    children = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
        except OSError:
            continue
        ppid = int(stat.rsplit(")", 1)[1].split()[1])
        children.setdefault(ppid, set()).add(int(entry.name))

    found, todo = set(), [pid]
    while todo:
        for child in children.get(todo.pop(), ()):
            if child not in found:
                found.add(child)
                todo.append(child)
    return found


def _is_alive(pid: int) -> bool:
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return False
    return "\nState:\tZ" not in status


def _main_window(pid: int) -> int | None:
    out = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--pid", str(pid)],
        capture_output=True, text=True, check=False,
    ).stdout.split()  # fmt: skip

    best, best_area = None, 0
    for window in out:
        geometry = subprocess.run(
            ["xdotool", "getwindowgeometry", "--shell", window],
            capture_output=True, text=True, check=False,
        ).stdout  # fmt: skip
        size = dict(line.split("=", 1) for line in geometry.split() if "=" in line)
        area = int(size.get("WIDTH", 0)) * int(size.get("HEIGHT", 0))
        if area > best_area:
            best, best_area = int(window), area
    return best


class _XClientMessage(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_int),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("message_type", ctypes.c_ulong),
        ("format", ctypes.c_int),
        ("data", ctypes.c_long * 5),
    ]


class _XEvent(ctypes.Union):
    _fields_ = [("xclient", _XClientMessage), ("pad", ctypes.c_long * 24)]


def _close_window(window: int):
    """What a window manager sends when its close button is clicked."""

    x11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11"))
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XOpenDisplay.argtypes = (ctypes.c_char_p,)
    x11.XInternAtom.restype = ctypes.c_ulong
    x11.XInternAtom.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int)
    x11.XSendEvent.argtypes = (
        ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long,
        ctypes.POINTER(_XEvent),
    )  # fmt: skip
    x11.XFlush.argtypes = (ctypes.c_void_p,)
    x11.XCloseDisplay.argtypes = (ctypes.c_void_p,)

    display = x11.XOpenDisplay(None)
    assert display, "no X display"
    try:
        event = _XEvent()
        event.xclient.type = 33  # ClientMessage
        event.xclient.display = display
        event.xclient.window = window
        event.xclient.message_type = x11.XInternAtom(display, b"WM_PROTOCOLS", 0)
        event.xclient.format = 32
        event.xclient.data[0] = x11.XInternAtom(display, b"WM_DELETE_WINDOW", 0)
        event.xclient.data[1] = 0  # CurrentTime
        x11.XSendEvent(display, window, 0, 0, ctypes.byref(event))
        x11.XFlush(display)
    finally:
        x11.XCloseDisplay(display)


def _wait(what, until, within):
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        value = until()
        if value:
            return value
        time.sleep(0.2)
    pytest.fail(f"not {what} within {within:g} s")


def _open(home: Path, clip: Path) -> subprocess.Popen:
    _settle(home)
    return subprocess.Popen(
        [sys.executable, "-m", "gridplayer", str(clip)],
        cwd=REPO,
        env=_env(home),
        stdout=(home / "app.out").open("wb"),
        stderr=subprocess.STDOUT,
    )


def _close_and_check(app: subprocess.Popen, home: Path):
    window = _wait("a window", lambda: _main_window(app.pid), OPEN_WITHIN_S)
    # the video's decoder process is up, so there is something to leave behind
    _wait(
        "the decoder process up",
        lambda: len(_descendants(app.pid)) >= 2,
        OPEN_WITHIN_S,
    )
    time.sleep(2)
    started = _descendants(app.pid)

    _close_window(window)

    try:
        code = app.wait(GONE_WITHIN_S)
    except subprocess.TimeoutExpired:
        log = (home / "app.out").read_text(errors="replace")[-2000:]
        pytest.fail(f"still running {GONE_WITHIN_S:g} s after closing\n{log}")
    finally:
        if app.poll() is None:
            for pid in (*_descendants(app.pid), app.pid):
                os.kill(pid, signal.SIGKILL)

    assert code == 0, "it took the exit watchdog, not the ordinary exit"
    _wait(
        "every process it started gone",
        lambda: not any(_is_alive(pid) for pid in started),
        3,
    )


def test_closing_the_window_ends_every_process(clip, home):
    _close_and_check(_open(home, clip), home)


def test_a_silent_client_on_the_instance_pipe_does_not_hold_it_up(clip, home):
    app = _open(home, clip)
    path = home / "rt" / "gridplayer" / "gridplayer-alabaster-fileopen.socket"
    _wait("the instance socket", path.exists, OPEN_WITHIN_S)

    silent = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    silent.connect(str(path))
    try:
        _close_and_check(app, home)
    finally:
        silent.close()
