"""The loop keys say what they did over the video: Shift+L, [ and ]."""

from functools import partial

import pytest
from PyQt5.QtWidgets import QApplication

from gridplayer.models.video import Video
from gridplayer.params.static import VideoEndAction
from gridplayer.utils.time_txt import loop_time_txt
from gridplayer.widgets.video_block import VideoBlock
from gridplayer.widgets.video_block_loop import LoopControl


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _block(mocker, **video_kwargs):
    block = mocker.Mock()
    block.is_live = False
    block.video_params = Video(uri="http://example.com/a.mp4", **video_kwargs)

    def set_end_action(action):
        block.video_params.end_action = action

    block.set_end_action.side_effect = set_end_action
    return block


def _said(block):
    return [c.args[0] for c in block.info_change.emit.call_args_list]


def test_shift_l_on_says_loop_file_on(mocker):
    block = _block(mocker, end_action=VideoEndAction.NEXT_FILE)

    VideoBlock.toggle_loop_file(block)

    assert block.video_params.end_action == VideoEndAction.LOOP_FILE
    assert _said(block) == ["Loop file: on"]


def test_shift_l_off_says_what_it_went_back_to(mocker):
    block = _block(mocker, end_action=VideoEndAction.SHUFFLE_FILE)

    VideoBlock.toggle_loop_file(block)
    VideoBlock.toggle_loop_file(block)

    assert block.video_params.end_action == VideoEndAction.SHUFFLE_FILE
    assert _said(block) == [
        "Loop file: on",
        "Loop file: off (back to play random file)",
    ]


def test_shift_l_with_nothing_to_go_back_to_still_says_on(mocker):
    block = _block(mocker, end_action=VideoEndAction.LOOP_FILE)

    VideoBlock.toggle_loop_file(block)

    assert block.video_params.end_action == VideoEndAction.LOOP_FILE
    assert _said(block) == ["Loop file: on"]


def test_live_says_nothing(mocker):
    block = _block(mocker, end_action=VideoEndAction.NEXT_FILE)
    block.is_live = True

    VideoBlock.toggle_loop_file(block)

    assert _said(block) == []


def _loop(mocker, time_ms, **video_kwargs):
    block = _block(mocker, **video_kwargs)
    block.time = time_ms
    block.video_driver.length = 60000
    loop = LoopControl(block)
    return block, loop


def test_loop_start_key_says_where(mocker):
    block, loop = _loop(mocker, 12345)

    loop.set_start()

    assert block.video_params.loop_start == 12345
    assert _said(block) == ["Loop start 0:12.3"]


def test_loop_end_key_says_where(mocker):
    block, loop = _loop(mocker, 75000)
    block.video_driver.length = 120000

    loop.set_end()

    assert block.video_params.loop_end == 75000
    assert _said(block) == ["Loop end 1:15.0"]


def test_loop_start_after_end_is_refused_quietly(mocker):
    block, loop = _loop(mocker, 30000, loop_end=20000)

    loop.set_start()

    assert block.video_params.loop_start != 30000
    assert _said(block) == []


@pytest.mark.parametrize(
    ("time_ms", "txt"),
    [(0, "0:00.0"), (12345, "0:12.3"), (61999, "1:01.9"), (3723400, "1:02:03.4")],
)
def test_loop_time_txt(time_ms, txt):
    assert loop_time_txt(time_ms) == txt
