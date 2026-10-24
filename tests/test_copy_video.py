"""Ctrl+C on a cell: its video copied as a file, to be pasted in a folder,
a chat, another player or this one."""

from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication

from gridplayer.params import env
from gridplayer.params.actions import ACTIONS
from gridplayer.params.menu import SECTIONS
from gridplayer.player.managers.locations import (
    DROP_EFFECT_COPY,
    DROP_EFFECT_MIME,
    LocationsManager,
    video_mime_data,
)
from gridplayer.utils.files import extract_mime_uris
from gridplayer.utils.keymap import default_keymap, find_duplicate_shortcuts

STREAM = "https://www.youtube.com/watch?v=abcdefghijk"


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def video(tmp_path):
    path = tmp_path / "clip one.mp4"
    path.touch()

    return path


@pytest.fixture
def clipboard():
    board = QApplication.clipboard()
    board.setText("untouched")

    return board


def _manager(uri):
    block = None
    if uri is not None:
        block = SimpleNamespace(video_params=SimpleNamespace(uri=uri))

    return LocationsManager(context=SimpleNamespace(active_block=block))


class TestTheAction:
    def test_on_ctrl_c(self):
        assert ACTIONS["Copy File"]["key"] == "Ctrl+C"
        assert ACTIONS["Copy File"]["func"] == "copy_active_video"

    def test_ctrl_c_is_no_other_one_s(self):
        keymap = default_keymap()

        assert [a for a, keys in keymap.items() if "Ctrl+C" in keys] == ["Copy File"]
        assert not find_duplicate_shortcuts(keymap)

    def test_first_in_the_file_submenu(self):
        file_menu = next(
            item
            for item in SECTIONS["video_active"]
            if isinstance(item, tuple) and item[0] == "File"
        )

        assert file_menu[1:3] == ("Copy File", "Copy File Name")

    def test_kept_with_the_other_locations(self):
        assert "copy_active_video" in _manager(None).commands


class TestTheMimeData:
    def test_a_file_as_a_file(self, video):
        data = video_mime_data(video)

        assert data.urls() == [QUrl.fromLocalFile(str(video))]
        assert data.urls()[0].toLocalFile() == video.as_posix()

    def test_a_file_as_its_path_for_text(self, video):
        assert video_mime_data(video).text() == str(video)

    @pytest.mark.skipif(not env.IS_WINDOWS, reason="Explorer only")
    def test_explorer_told_to_paste_a_copy(self, video):
        data = video_mime_data(video)

        assert bytes(data.data(DROP_EFFECT_MIME)) == b"\x01\x00\x00\x00"

    @pytest.mark.skipif(env.IS_WINDOWS, reason="away from Windows")
    def test_no_drop_effect_away_from_windows(self, video):
        assert not video_mime_data(video).hasFormat(DROP_EFFECT_MIME)

    def test_copy_is_one_as_a_dword(self):
        assert DROP_EFFECT_COPY == b"\x01\x00\x00\x00"

    def test_a_link_as_a_link(self):
        data = video_mime_data(STREAM)

        assert [url.toString() for url in data.urls()] == [STREAM]
        assert data.text() == STREAM
        assert not data.hasFormat(DROP_EFFECT_MIME)

    def test_pasted_back_in_the_same_video(self, video):
        assert extract_mime_uris(video_mime_data(video)) == [video.as_posix()]
        assert extract_mime_uris(video_mime_data(STREAM)) == [STREAM]


class TestWhatIsCopied:
    def test_the_active_file(self, clipboard, video):
        _manager(video).cmd_copy_active_video()

        data = clipboard.mimeData()
        assert [url.toLocalFile() for url in data.urls()] == [video.as_posix()]
        assert data.text() == str(video)

    def test_the_active_link(self, clipboard):
        _manager(STREAM).cmd_copy_active_video()

        assert clipboard.text() == STREAM

    def test_nothing_without_a_video(self, clipboard):
        _manager(None).cmd_copy_active_video()

        assert clipboard.text() == "untouched"

    def test_a_file_gone_still_has_its_path(self, clipboard, tmp_path):
        gone = tmp_path / "gone.mp4"

        _manager(gone).cmd_copy_active_video()

        assert clipboard.text() == str(gone)
