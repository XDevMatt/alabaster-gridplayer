"""Single mode left and entered again before a hidden cell's unpause lands."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.models.video import Video
from gridplayer.params.static import VideoInitialState
from gridplayer.player.managers.single_mode import SingleModeManager
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.settings import Settings
from gridplayer.widgets.video_block import VideoBlock


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path):
    settings = Settings()
    real_settings = settings.settings
    settings.settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)
    PlaylistSettings().clear()

    yield

    PlaylistSettings().clear()
    settings.settings = real_settings


class _Driver:
    """VLC as far as pause goes: it is asked, and it answers when told."""

    def __init__(self):
        self.is_video_initialized = True
        self.asked = []

    def set_pause(self, paused):
        self.asked.append(bool(paused))


def _context():
    context = MagicMock()
    context.is_drag_ui = False
    context.is_disable_overlay = False
    context.is_overlay_hide_on_timeout = False
    context.is_show_overlay_border = False
    context.overlay_timeout = 1
    return context


def _cell(parent, uri, playing):
    block = VideoBlock(video_driver=MagicMock(), context=_context(), parent=parent)
    block.video_params = Video(
        uri=uri,
        playback_state=(
            VideoInitialState.PLAYING if playing else VideoInitialState.PAUSED
        ),
    )
    block.video_driver = _Driver()
    return block


def _manager(shown, hidden):
    ctx = SimpleNamespace(
        is_single_mode=False,
        is_pause_background_videos=True,
        active_block=shown,
        video_blocks=[shown, hidden],
        commands=SimpleNamespace(grid_cell_count=lambda: 2),
    )
    manager = SingleModeManager(context=ctx)
    manager._ctx.is_pause_background_videos = True
    return manager


def _release(*blocks):
    for block in blocks:
        block.url_resolver.cleanup()


def test_leaving_and_entering_again_before_the_unpause_lands_ends_paused():
    """Cell 2 is hidden and playing. Leave single mode and go straight back.

    Its unpause has not been confirmed, so the pause on the way back in
    has to wait. Once VLC reports the unpause, the cell is paused, and
    leaving single mode again lets it play.
    """

    parent = QWidget()
    shown = _cell(parent, "http://example.com/picture.mp4", playing=True)
    hidden = _cell(parent, "http://example.com/music.mp3", playing=True)
    manager = _manager(shown, hidden)

    try:
        manager.single_mode_on()
        hidden.playback_status_changed(True)

        manager.single_mode_off()
        manager.single_mode_on()

        assert hidden.video_driver.asked == [True, False]

        hidden.playback_status_changed(False)

        assert hidden.video_driver.asked[-1] is True
        hidden.playback_status_changed(True)
        assert hidden.video_params.is_paused

        manager.single_mode_off()

        assert hidden.video_driver.asked[-1] is False
        hidden.playback_status_changed(False)
        assert not hidden.video_params.is_paused
    finally:
        _release(shown, hidden)


def test_a_pause_during_an_unpause_lands_when_the_unpause_is_reported():
    """set_pause(True) while an unpause has not landed yet.

    When VLC then says the video is playing, the pause is what is sent,
    and the cell is paused once VLC says that too.
    """

    parent = QWidget()
    block = _cell(parent, "http://example.com/music.mp3", playing=False)

    try:
        block.set_pause(False)
        block.set_pause(True)

        assert block.video_driver.asked == [False]

        block.playback_status_changed(False)

        assert block.video_driver.asked == [False, True]
        block.playback_status_changed(True)
        assert block.video_params.is_paused
    finally:
        _release(block)


def test_a_viewer_paused_hidden_cell_stays_paused():
    """On, off, on. A cell the viewer had paused is not started."""

    parent = QWidget()
    shown = _cell(parent, "http://example.com/picture.mp4", playing=True)
    hidden = _cell(parent, "http://example.com/music.mp3", playing=False)
    manager = _manager(shown, hidden)

    try:
        manager.single_mode_on()
        manager.single_mode_off()
        manager.single_mode_on()

        assert hidden.video_driver.asked == []
        assert hidden.video_params.is_paused
    finally:
        _release(shown, hidden)
