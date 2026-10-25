"""End of a pass: a file that finishes still loops, a stall that repeats does not."""

from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from gridplayer.models.video import Video
from gridplayer.settings import Settings
from gridplayer.vlc_player.player_base import (
    DEAD_INPUT_PASSES,
    RESTART_REAPPLY_TRIES,
    VlcPlayerBase,
)
from gridplayer.vlc_player.static import MediaInput

NEXT_URI = "http://example.com/next.mp4"


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def _isolated_settings(tmp_path):
    settings = Settings()
    real_settings = settings.settings

    settings.settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)

    yield

    settings.settings = real_settings


class _Player(VlcPlayerBase):
    def notify_update_status(self, status, percent=0): ...
    def notify_error(self, error, vlc_lines=()): ...
    def notify_time_changed(self, new_time): ...
    def notify_playback_status_changed(self, new_status): ...
    def notify_load_video_done(self, media_track): ...
    def notify_snapshot_taken(self, snapshot_path): ...
    def loopback_load_video_st2_set_media(self): ...
    def loopback_load_video_st3_extract_media_track(self): ...
    def loopback_load_video_st4_loaded(self): ...


class _FakeEventManager:
    def event_attach(self, event_type, callback): ...


class _FakeMedia:
    def event_manager(self):
        return _FakeEventManager()

    def add_options(self, *options): ...


class _FakeInstance:
    def media_new(self, uri):
        return _FakeMedia()

    def media_new_path(self, uri):
        return _FakeMedia()


def _player(last_time):
    player = _Player(vlc_instance=_FakeInstance())
    player.is_video_initialized = True
    player._last_time = last_time
    player.errors = []
    player.notify_error = lambda error, vlc_lines: player.errors.append(error)
    return player


def _next_file():
    return MediaInput(
        uri=NEXT_URI,
        is_live=False,
        is_audio_only=False,
        size=(640, 360),
        video=Video(uri=NEXT_URI),
    )


def _time(value):
    return SimpleNamespace(u=SimpleNamespace(new_time=value))


def _buffering(value):
    return SimpleNamespace(u=SimpleNamespace(new_cache=value))


def _wait_out(player):
    """The dead-input passes that leave a stall to run out."""

    for _ in range(DEAD_INPUT_PASSES):
        player.cb_buffering(_buffering(0.0))


def test_a_stall_waited_out_twice_is_an_error():
    """A truncated file restarts at the same time, pass after pass.

    The first time it is left to start over. The second time it froze no
    further on, so that is an error instead of another restart.
    """

    player = _player(last_time=2500)

    _wait_out(player)
    player.cb_end_reached(None)

    assert player.errors == []
    assert player._restart_reapply_tries == RESTART_REAPPLY_TRIES
    assert player._stall_freeze_point == 2500

    for moment in (100, 1000, 2500):
        player.cb_time_changed(_time(moment))

    _wait_out(player)
    player.cb_end_reached(None)

    assert player.errors == ["Video stopped unexpectedly"]
    assert player._restart_reapply_tries == 0


def test_a_normal_end_still_loops():
    """Reaching the end of a file that was playing starts the next pass."""

    player = _player(last_time=None)

    for moment in (500, 4000, 9000):
        player.cb_time_changed(_time(moment))

    player.cb_end_reached(None)

    assert player.errors == []
    assert player._restart_reapply_tries == RESTART_REAPPLY_TRIES


@pytest.mark.parametrize("left_behind", ["freeze", "gave_up"])
@pytest.mark.usefixtures("_isolated_settings")
def test_a_stall_does_not_carry_into_the_next_file(left_behind):
    """A stall on one file does not fail the next file loaded in the cell.

    Waiting a stall out leaves a freeze. Waiting it out again gives up.
    Neither stays after another file is loaded, so that file's first
    waited-out end restarts it. The restart counter is cleared here so
    the next end is what arms it.
    """

    player = _player(last_time=2500)

    _wait_out(player)
    player.cb_end_reached(None)

    if left_behind == "gave_up":
        for moment in (100, 1000, 2500):
            player.cb_time_changed(_time(moment))

        _wait_out(player)
        player.cb_end_reached(None)

        assert player._stall_gave_up
        assert player.errors == ["Video stopped unexpectedly"]
    else:
        assert player._stall_has_freeze
        assert player._stall_freeze_point == 2500
        assert not player._stall_gave_up
        assert player.errors == []

    player.errors.clear()
    player.load_video(_next_file())

    assert player.errors == []
    assert not player._pass_waited_out
    assert player._stall_freeze_point is None
    assert not player._stall_has_freeze
    assert not player._stall_gave_up

    player.is_video_initialized = True
    player._last_time = 1800
    player._restart_reapply_tries = 0

    _wait_out(player)
    player.cb_end_reached(None)

    assert player.errors == []
    assert player._restart_reapply_tries == RESTART_REAPPLY_TRIES
    assert player._stall_has_freeze
    assert player._stall_freeze_point == 1800
    assert not player._stall_gave_up
