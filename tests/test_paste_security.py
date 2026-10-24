"""What is pasted, dropped or handed over by another process: only the
kinds of links a cell plays, nothing on another computer, and no more of
it than is worth looking at. And the test run itself, kept away from the
settings of whoever runs it."""

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt5.QtCore import QMimeData, QUrl
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.params.static import UnsavedChangesMode
from gridplayer.player.managers.actions import ActionsManager
from gridplayer.settings import _default_settings, _Settings
from gridplayer.utils import files, single_instance
from gridplayer.utils.app_dir import ENV_USER_DATA_DIR, get_app_data_dir
from gridplayer.utils.files import (
    MAX_MIME_ITEMS,
    extract_mime_uris,
    is_allowed_url,
    is_remote_share,
)


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _text(text: str) -> QMimeData:
    data = QMimeData()
    data.setText(text)

    return data


def _urls(*urls: str) -> QMimeData:
    data = QMimeData()
    data.setUrls([QUrl(url) for url in urls])

    return data


@pytest.fixture
def untouched(mocker):
    """Whether a path was looked at on disk: for one on another computer,
    looking is what sends the password's hash there."""

    return mocker.patch.object(files.Path, "is_dir", side_effect=AssertionError)


class TestShares:
    @pytest.mark.parametrize(
        "path",
        [
            r"\\host\share\a.mp4",
            "//host/share/a.mp4",
            r"\\10.0.0.5\share\a.mp4",
            r"\\?\UNC\host\share\a.mp4",
        ],
    )
    def test_on_another_computer(self, path):
        assert is_remote_share(path)

    @pytest.mark.parametrize(
        "path",
        [
            r"C:\Videos\a.mp4",
            r"\\?\C:\Videos\a.mp4",
            r"\\.\pipe\x",
            r"\\localhost\c$\a.mp4",
            "a.mp4",
        ],
    )
    def test_on_this_one(self, path):
        assert not is_remote_share(path)

    def test_pasted_as_text_never_looked_at(self, untouched):
        assert extract_mime_uris(_text(r"\\host\share\a.mp4")) == []

    def test_dropped_as_a_file_link_never_looked_at(self, untouched):
        assert extract_mime_uris(_urls("file://host/share/a.mp4")) == []

    def test_a_file_link_as_text_never_looked_at(self, untouched):
        assert extract_mime_uris(_text("file://host/share/a.mp4")) == []

    def test_handed_over_never_looked_at(self, mocker):
        mocker.patch.object(single_instance.Path, "exists", side_effect=AssertionError)

        assert single_instance.validate_open_items([r"\\host\share\a.mp4"]) == []


class TestLinks:
    @pytest.mark.parametrize(
        "url",
        [
            "smb://host/share/a.mp4",
            "file://host/share/a.mp4",
            "javascript://alert(1)",
            "data://text/plain,x",
            "ms-msdt://x",
            "vlc://x",
        ],
    )
    def test_left_out(self, url):
        assert not is_allowed_url(url)
        assert extract_mime_uris(_text(url)) == []
        assert extract_mime_uris(_urls(url)) == []

    @pytest.mark.parametrize(
        "url", ["https://example.com/a.mp4", "http://a/b", "rtsp://cam/1"]
    )
    def test_taken(self, url):
        assert extract_mime_uris(_text(url)) == [url]

    def test_a_local_file_link_as_text_is_the_file(self, tmp_path):
        clip = tmp_path / "a.mp4"
        clip.touch()

        uri = QUrl.fromLocalFile(str(clip)).toString()

        assert extract_mime_uris(_text(uri)) == [clip.as_posix()]

    def test_no_leading_dash_reaches_a_resolver_as_a_link(self):
        # yt-dlp and Streamlink are handed links only, and a link starts
        # with its scheme
        assert extract_mime_uris(_text("--exec calc")) == []


class TestHugePastes:
    def test_no_more_lines_than_the_most_looked_at(self):
        text = "\n".join(f"https://example.com/{n}.mp4" for n in range(5000))

        assert len(extract_mime_uris(_text(text))) == MAX_MIME_ITEMS

    def test_no_more_links_than_the_most_looked_at(self):
        urls = [f"https://example.com/{n}.mp4" for n in range(MAX_MIME_ITEMS + 50)]

        assert len(extract_mime_uris(_urls(*urls))) == MAX_MIME_ITEMS

    def test_a_giant_line_is_nothing(self):
        assert extract_mime_uris(_text("x" * 5_000_000)) == []


def test_held_ctrl_v_does_not_repeat():
    commands = MagicMock()
    ctx = SimpleNamespace(commands=commands)
    parent = QWidget()

    manager = ActionsManager(context=ctx, parent=parent)

    assert ctx.actions["Add - Clipboard"].autoRepeat() is False
    # every other key repeats as ever: seeking, volume
    assert ctx.actions["Copy File"].autoRepeat() is True

    manager.deleteLater()
    parent.deleteLater()


class TestTheRunsOwnData:
    """No test reaches the player's real settings: a run that did once left
    the player asking about unsaved changes on close."""

    def test_the_data_folder_is_the_runs(self):
        folder = Path(os.environ[ENV_USER_DATA_DIR])

        assert get_app_data_dir() == folder
        assert folder.name.startswith("gridplayer-tests-")

    def test_settings_are_written_there(self):
        path = Path(_Settings().settings.fileName())

        assert Path(os.environ[ENV_USER_DATA_DIR]) in path.parents
        assert "GridPlayer-Alabaster" not in path.parts


def test_closing_never_asks_out_of_the_box():
    assert _default_settings["playlist/unsaved_changes"] is UnsavedChangesMode.DISCARD


class TestInvalidLinks:
    def test_one_qt_cannot_read_is_not_the_working_folder(self):
        # QUrl gives "" for it, which as a path is the folder the player
        # runs in
        assert extract_mime_uris(_urls("javascript://alert(1)")) == []
