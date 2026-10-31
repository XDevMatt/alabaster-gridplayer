"""A dropped folder follows Include subfolders."""

import pytest

from gridplayer.utils import folder_navigator
from tests.conftest import FakeSettings


@pytest.mark.parametrize("is_recursive", [True, False])
def test_scan_rules_carry_include_subfolders(monkeypatch, is_recursive):
    values = {
        "playlist/folder_skip_hidden": True,
        "playlist/folder_max_entries": 0,
        "video_defaults/dir_recursive": is_recursive,
    }
    monkeypatch.setattr(
        folder_navigator, "PlaylistSettings", lambda: FakeSettings(values)
    )

    assert folder_navigator.scan_rules().is_folder_recursive is is_recursive


def test_include_subfolders_is_on_by_default():
    from gridplayer.settings import _default_settings

    assert _default_settings["video_defaults/dir_recursive"] is True
