"""End of a pass: a file that finishes still loops, a stall that repeats does not."""

from types import SimpleNamespace

import pytest
from PyQt5.QtWidgets import QApplication

from gridplayer.vlc_player.player_base import (
    DEAD_INPUT_PASSES,
    RESTART_REAPPLY_TRIES,
    VlcPlayerBase,
)


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


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


def _player(last_time):
    player = _Player(vlc_instance=None)
    player.is_video_initialized = True
    player._last_time = last_time
    player.errors = []
    player.notify_error = lambda error, vlc_lines: player.errors.append(error)
    return player


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
