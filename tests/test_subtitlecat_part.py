"""The cell command imports the plugin only when it is on."""

import subprocess
import sys
from unittest.mock import Mock

from gridplayer.widgets.video_block_subtitlecat import SubtitleCatControl


def test_importing_the_part_does_not_import_the_plugin():
    script = (
        "import sys\n"
        "import gridplayer.widgets.video_block_subtitlecat\n"
        "banned = (\n"
        "    'gridplayer.plugins.subtitlecat',\n"
        "    'streamlink',\n"
        "    'yt_dlp',\n"
        ")\n"
        "found = [name for name in banned if name in sys.modules]\n"
        "print('\\n'.join(found))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""


def test_find_while_off_does_not_import_the_plugin(monkeypatch):
    monkeypatch.setattr("gridplayer.plugins.Settings", lambda: _Off())
    saved = _drop_plugin_modules()
    block = Mock()

    try:
        assert SubtitleCatControl(block).find() is None
        assert "gridplayer.plugins.subtitlecat" not in sys.modules
    finally:
        sys.modules.update(saved)


def test_find_while_on_opens_the_dialog(monkeypatch):
    monkeypatch.setattr("gridplayer.plugins.Settings", lambda: _On())
    import gridplayer.plugins.subtitlecat.dialog as dialog_mod

    opened = []

    class FakeDialog:
        def __init__(self, block, parent=None, client=None, settings_get=None):
            opened.append(block)

        def exec_(self):
            opened.append("exec")

    monkeypatch.setattr(dialog_mod, "SubtitleCatDialog", FakeDialog)
    block = Mock()

    assert SubtitleCatControl(block).find() is None
    assert opened == [block, "exec"]


def _drop_plugin_modules():
    saved = {}

    for name in list(sys.modules):
        if name == "gridplayer.plugins.subtitlecat" or name.startswith(
            "gridplayer.plugins.subtitlecat."
        ):
            saved[name] = sys.modules.pop(name)

    return saved


class _Off:
    def get(self, key):
        if key == "plugins/subtitlecat":
            return False
        raise KeyError(key)


class _On:
    def get(self, key):
        if key == "plugins/subtitlecat":
            return True
        raise KeyError(key)
