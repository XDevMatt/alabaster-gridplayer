from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.widgets.video_block import VideoBlock
from gridplayer.widgets.video_overlay import OverlayBlock


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def overlay():
    overlay = OverlayBlock()
    overlay.resize(400, 300)
    overlay.set_label("a video.mp4")
    overlay.show()
    QApplication.processEvents()
    yield overlay
    overlay.close()


def _global_center(widget):
    return widget.mapToGlobal(widget.rect().center())


def _double_click(global_pos, button=Qt.LeftButton):
    return QMouseEvent(
        QEvent.MouseButtonDblClick,
        QPointF(0, 0),
        QPointF(global_pos),
        button,
        button,
        Qt.NoModifier,
    )


def test_the_title_is_on_the_title_strip(overlay):
    assert overlay.is_title_at(_global_center(overlay.label_text))


def test_the_middle_of_the_picture_is_not(overlay):
    assert not overlay.is_title_at(_global_center(overlay))
    # down by the bottom bar
    assert not overlay.is_title_at(overlay.mapToGlobal(QPoint(200, 290)))


def test_no_title_while_the_chrome_is_hidden(overlay):
    overlay.set_is_chrome_visible(False)

    assert not overlay.is_title_at(_global_center(overlay.label_text))


def _block(mocker, *, is_on_title, is_disable_clicks=False):
    block = mocker.Mock()
    block._ctx = SimpleNamespace(
        is_disable_mouse_click_events=is_disable_clicks,
        commands=mocker.Mock(),
    )
    block.overlay.is_title_at.return_value = is_on_title
    block._dispatch_mouse_action.return_value = True
    return block


def test_double_click_on_the_title_toggles_single_mode_for_the_cell(mocker):
    block = _block(mocker, is_on_title=True)
    event = _double_click(QPoint(10, 10))

    VideoBlock.mouseDoubleClickEvent(block, event)

    block._ctx.commands.toggle_single_video_for.assert_called_once_with(block)
    block._dispatch_mouse_action.assert_not_called()
    assert event.isAccepted()


def test_double_click_on_the_picture_does_what_it_is_bound_to(mocker):
    block = _block(mocker, is_on_title=False)

    VideoBlock.mouseDoubleClickEvent(block, _double_click(QPoint(10, 10)))

    block._ctx.commands.toggle_single_video_for.assert_not_called()
    block._dispatch_mouse_action.assert_called_once()


def test_right_double_click_on_the_title_is_left_to_the_keymap(mocker):
    block = _block(mocker, is_on_title=True)

    VideoBlock.mouseDoubleClickEvent(
        block, _double_click(QPoint(10, 10), button=Qt.RightButton)
    )

    block._ctx.commands.toggle_single_video_for.assert_not_called()
    block._dispatch_mouse_action.assert_called_once()


def test_no_title_double_click_with_mouse_clicks_off(mocker):
    block = _block(mocker, is_on_title=True, is_disable_clicks=True)

    VideoBlock.mouseDoubleClickEvent(block, _double_click(QPoint(10, 10)))

    block._ctx.commands.toggle_single_video_for.assert_not_called()
