"""Plugins stay unloaded until their setting is on."""

import subprocess
import sys

import pytest

from gridplayer.plugins import CATALOG, load
from gridplayer.settings import _default_settings


def test_subtitlecat_is_off_by_default():
    assert _default_settings["plugins/subtitlecat"] is False
    assert _default_settings["plugins/subtitlecat_translate"] is False


def test_the_catalog_names_subtitlecat_and_not_streamlink():
    assert [spec.id for spec in CATALOG] == ["subtitlecat"]
    assert CATALOG[0].module == "gridplayer.plugins.subtitlecat"
    assert CATALOG[0].setting == "plugins/subtitlecat"
    assert CATALOG[0].kind == "subtitles"
    assert all("streamlink" not in spec.module for spec in CATALOG)


def test_load_when_off_does_not_import(monkeypatch):
    monkeypatch.setattr("gridplayer.plugins.Settings", lambda: _Store(False))

    def refuse(name):
        raise AssertionError(name)

    monkeypatch.setattr("gridplayer.plugins.importlib.import_module", refuse)

    assert load("subtitlecat") is None
    assert load("streamlink") is None


def test_load_when_on_imports_the_package_but_not_the_client(monkeypatch):
    monkeypatch.setattr("gridplayer.plugins.Settings", lambda: _Store(True))
    imported = []
    real_import = __import__("importlib").import_module

    def spy(name):
        imported.append(name)
        return real_import(name)

    monkeypatch.setattr("gridplayer.plugins.importlib.import_module", spy)

    module = load("subtitlecat")

    assert module.PLUGIN_ID == "subtitlecat"
    assert imported == ["gridplayer.plugins.subtitlecat"]


def test_a_fresh_interpreter_does_not_import_the_plugin_or_yt_dlp():
    script = (
        "import sys\n"
        "import gridplayer.plugins\n"
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


class _Store:
    def __init__(self, enabled):
        self._enabled = enabled

    def get(self, key):
        if key == "plugins/subtitlecat":
            return self._enabled
        raise KeyError(key)


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("psutil") is None,
    reason="psutil is not installed",
)
def test_importing_the_client_does_not_listen():
    script = (
        "import psutil\n"
        "def listening():\n"
        "    found = []\n"
        "    for conn in psutil.Process().net_connections(kind='inet'):\n"
        "        if conn.status in {'LISTEN', 'BOUND'}:\n"
        "            found.append((str(conn.laddr), conn.status))\n"
        "    return found\n"
        "before = listening()\n"
        "from gridplayer.plugins.subtitlecat.client import SubtitleCatClient\n"
        "SubtitleCatClient(settings_get=lambda key: False)\n"
        "after = listening()\n"
        "new = [item for item in after if item not in before]\n"
        "print(len(new))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0"
