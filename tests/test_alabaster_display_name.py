"""User-visible restart, tray and VLC-missing strings name the fork."""

from pathlib import Path

from gridplayer.version import __display_name__

ROOT = Path(__file__).resolve().parents[1]


def test_the_display_name_is_the_forks():
    assert __display_name__ == "GridPlayer Alabaster"


def test_the_restart_message_names_the_fork():
    source = (ROOT / "gridplayer/player/managers/settings.py").read_text(
        encoding="utf-8"
    )

    assert "{APP}" in source
    assert "__display_name__" in source
    assert "restart GridPlayer." not in source


def test_the_tray_still_running_note_names_the_fork():
    source = (ROOT / "gridplayer/player/managers/tray.py").read_text(encoding="utf-8")

    assert "__display_name__" in source
    assert "GridPlayer is still running" not in source


def test_the_vlc_missing_error_names_the_fork():
    source = (ROOT / "gridplayer/main/run.py").read_text(encoding="utf-8")

    assert "__display_name__" in source
    assert '"GridPlayer"' not in source
    assert "GridPlayer plays videos with VLC" not in source
