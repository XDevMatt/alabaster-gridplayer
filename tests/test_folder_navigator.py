"""A dropped folder follows Include subfolders and Files to play."""

import pytest

from gridplayer.params.static import MediaKind
from gridplayer.utils import folder_navigator
from tests.conftest import FakeSettings


@pytest.mark.parametrize("is_recursive", [True, False])
def test_scan_rules_carry_include_subfolders(monkeypatch, is_recursive):
    values = {
        "playlist/folder_skip_hidden": True,
        "playlist/folder_max_entries": 0,
        "video_defaults/dir_recursive": is_recursive,
        "video_defaults/media_kind": MediaKind.VIDEOS_ONLY,
    }
    monkeypatch.setattr(
        folder_navigator, "PlaylistSettings", lambda: FakeSettings(values)
    )

    assert folder_navigator.scan_rules().is_folder_recursive is is_recursive


def test_include_subfolders_is_on_by_default():
    from gridplayer.settings import _default_settings

    assert _default_settings["video_defaults/dir_recursive"] is True


@pytest.mark.parametrize("kind", list(MediaKind))
def test_scan_rules_carry_files_to_play(monkeypatch, kind):
    values = {
        "playlist/folder_skip_hidden": True,
        "playlist/folder_max_entries": 0,
        "video_defaults/dir_recursive": True,
        "video_defaults/media_kind": kind,
    }
    monkeypatch.setattr(
        folder_navigator, "PlaylistSettings", lambda: FakeSettings(values)
    )

    assert folder_navigator.scan_rules().media_kind is kind
