"""Alabaster keys that do something new: C and X a 5% speed step, M mutes
every cell (or unmutes them all), Esc leaves fullscreen before it minimizes."""

from functools import partial
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gridplayer.params.actions import ACTIONS
from gridplayer.params.static import MAX_RATE, MIN_RATE
from gridplayer.player.managers.video_blocks import VideoBlocksManager
from gridplayer.player.managers.window_state import WindowStateManager
from gridplayer.widgets.video_block import RATE_STEP, VideoBlock

# ---------------------------------------------------------------------------
# speed


def _rated(rate):
    return SimpleNamespace(
        is_video_initialized=True,
        is_live=False,
        video_params=SimpleNamespace(rate=rate),
        set_rate=Mock(),
    )


class TestSpeedStep:
    def test_five_percent(self):
        assert RATE_STEP == 0.05

    @pytest.mark.parametrize(
        ("rate", "faster", "slower"), [(1.0, 1.05, 0.95), (1.1, 1.15, 1.05)]
    )
    def test_a_press(self, rate, faster, slower):
        block = _rated(rate)
        VideoBlock.rate_increase(block)
        block.set_rate.assert_called_once_with(faster)

        block = _rated(rate)
        VideoBlock.rate_decrease(block)
        block.set_rate.assert_called_once_with(slower)

    def test_no_drift(self):
        block = _rated(1.0)
        block.set_rate.side_effect = lambda rate: None

        for n in range(1, 41):
            VideoBlock.rate_increase(block)
            assert block.video_params.rate == round(1.0 + n * 0.05, 2)

        for n in range(39, -1, -1):
            VideoBlock.rate_decrease(block)
            assert block.video_params.rate == round(1.0 + n * 0.05, 2)

    def test_kept_between_min_and_max(self):
        block = _rated(MIN_RATE)
        VideoBlock.rate_decrease(block)
        assert block.video_params.rate == MIN_RATE

        block = _rated(MAX_RATE)
        VideoBlock.rate_increase(block)
        assert block.video_params.rate == MAX_RATE

    def test_the_keys(self):
        assert ACTIONS["Faster"]["func"][-1] == "rate_increase"
        assert ACTIONS["Slower"]["func"][-1] == "rate_decrease"
        assert ACTIONS["Normal"]["func"][-1] == "rate_reset"


# ---------------------------------------------------------------------------
# M: mute all


def _manager(*muted):
    manager = SimpleNamespace(
        _ctx=SimpleNamespace(
            video_blocks=[
                SimpleNamespace(video_params=SimpleNamespace(is_muted=m)) for m in muted
            ]
        ),
        all_set_muted=Mock(),
    )
    manager.is_all_videos_param_set_to = partial(
        VideoBlocksManager.is_all_videos_param_set_to, manager
    )
    return manager


class TestMuteAll:
    @pytest.mark.parametrize(
        ("muted", "to"),
        [
            ((False, False), True),
            ((True, False), True),
            ((True, True), False),
            ((True,), False),
        ],
    )
    def test_mutes_every_one_unless_they_all_are(self, muted, to):
        manager = _manager(*muted)

        VideoBlocksManager.cmd_all_mute_unmute(manager)

        manager.all_set_muted.emit.assert_called_once_with(to)

    def test_the_action(self):
        action = ACTIONS["Audio Volume - Mute / Unmute [ALL]"]

        assert action["key"] == "M"
        assert action["func"] == "all_mute_unmute"
        assert action["toggle"] == ("is_all_videos_param_set_to", "is_muted", True)


# ---------------------------------------------------------------------------
# Esc


class TestEsc:
    @staticmethod
    def _manager(is_fullscreen):
        window = Mock()
        window.isFullScreen.return_value = is_fullscreen
        manager = SimpleNamespace(parent=lambda: window, cmd_fullscreen=Mock())
        return manager, window

    def test_leaves_fullscreen(self):
        manager, window = self._manager(is_fullscreen=True)

        WindowStateManager.cmd_escape(manager)

        manager.cmd_fullscreen.assert_called_once_with()
        window.showMinimized.assert_not_called()

    def test_minimizes_otherwise(self):
        manager, window = self._manager(is_fullscreen=False)

        WindowStateManager.cmd_escape(manager)

        window.showMinimized.assert_called_once_with()
        manager.cmd_fullscreen.assert_not_called()

    def test_the_actions(self):
        assert ACTIONS["Leave Fullscreen or Minimize"]["key"] == "Esc"
        assert ACTIONS["Leave Fullscreen or Minimize"]["func"] == "escape"
        # the menu item still only minimizes, it just has no key
        assert ACTIONS["Minimize"]["func"] == "minimize"
        assert "key" not in ACTIONS["Minimize"]
