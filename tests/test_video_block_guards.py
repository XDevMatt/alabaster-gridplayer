"""The guards on a video block's commands ask the block, whether the command
is the block's own or one of a part of it."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt5 import sip
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.widgets.video_block import VideoBlock
from gridplayer.widgets.video_block_guards import (
    VideoBlockPart,
    only_initialized,
    only_seekable,
)


class _Part(VideoBlockPart):
    @only_initialized
    @only_seekable
    def command(self):
        return "done"


class _Block:
    def __init__(self, *, is_video_initialized, is_live):
        self.is_video_initialized = is_video_initialized
        self.is_live = is_live

    @only_initialized
    @only_seekable
    def command(self):
        return "done"


@pytest.mark.parametrize(
    ("is_video_initialized", "is_live", "result"),
    [
        (True, False, "done"),
        (False, False, None),
        (True, True, None),
    ],
)
def test_a_part_is_guarded_by_its_block(is_video_initialized, is_live, result):
    block = SimpleNamespace(is_video_initialized=is_video_initialized, is_live=is_live)

    assert _Part(block).command() == result


@pytest.mark.parametrize(
    ("is_video_initialized", "is_live", "result"),
    [
        (True, False, "done"),
        (False, False, None),
        (True, True, None),
    ],
)
def test_the_block_is_guarded_by_itself(is_video_initialized, is_live, result):
    block = _Block(is_video_initialized=is_video_initialized, is_live=is_live)

    assert block.command() == result


def test_a_part_asks_its_block_not_itself():
    block = SimpleNamespace(is_video_initialized=False, is_live=False)
    part = _Part(block)

    # what the part itself would say is not asked
    part.is_video_initialized = True

    assert part.command() is None


class _QtBlock(QWidget):
    is_video_initialized = True
    is_live = False

    @only_initialized
    def command(self):
        return "done"


@pytest.fixture(scope="module")
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.mark.usefixtures("_qapp")
def test_a_closed_qt_block_is_left_alone():
    block = _QtBlock()
    command = block.command
    assert command() == "done"

    sip.delete(block)

    assert command() is None


def test_a_stand_in_specced_as_a_video_block_is_never_closed():
    block = Mock(spec=VideoBlock)
    block.is_video_initialized = True
    block.is_live = False

    assert only_initialized(lambda b: "done")(block) == "done"
