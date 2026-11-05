"""The mouse side buttons still work with "Disable mouse click events" on.

That setting is for clicks on the picture (pause, single mode). The side
buttons are pressed like keys, mapped to next and previous file, say.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt5.QtCore import QEvent, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.player.managers.actions import ActionsManager
from gridplayer.utils.keymap import MouseButtonSequence
from gridplayer.widgets.video_block import VideoBlock


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _release(button):
    return QMouseEvent(
        QEvent.MouseButtonRelease,
        QPointF(0, 0),
        QPointF(0, 0),
        button,
        Qt.NoButton,
        Qt.NoModifier,
    )


def _manager(is_disable_clicks):
    manager = Mock()
    manager._ctx = SimpleNamespace(
        is_disable_mouse_click_events=is_disable_clicks,
        is_disable_mouse_wheel_events=False,
        commands=SimpleNamespace(handle_fake_drag_click=lambda event: False),
    )
    manager._mouse_index = {
        "Click": "Play / Pause",
        "Back-Click": "Play Previous File",
        "Forward-Click": "Play Next File",
    }
    manager.trigger.return_value = True
    return manager


@pytest.mark.parametrize(
    ("button", "action_id"),
    [
        (Qt.BackButton, "Play Previous File"),
        (Qt.ForwardButton, "Play Next File"),
    ],
)
def test_side_buttons_fire_with_clicks_disabled(button, action_id):
    manager = _manager(is_disable_clicks=True)

    assert ActionsManager.handle_mouse_event(manager, _release(button))

    manager.trigger.assert_called_once_with(action_id)


def test_a_left_click_still_does_nothing_with_clicks_disabled():
    manager = _manager(is_disable_clicks=True)

    assert not ActionsManager.handle_mouse_event(manager, _release(Qt.LeftButton))

    manager.trigger.assert_not_called()


def test_a_left_click_works_with_clicks_enabled():
    manager = _manager(is_disable_clicks=False)

    assert ActionsManager.handle_mouse_event(manager, _release(Qt.LeftButton))

    manager.trigger.assert_called_once_with("Play / Pause")


@pytest.mark.parametrize(
    ("button", "is_dispatched"),
    [(Qt.BackButton, True), (Qt.ForwardButton, True), (Qt.LeftButton, False)],
)
def test_a_cell_passes_on_only_side_buttons_with_clicks_disabled(
    mocker, button, is_dispatched
):
    block = mocker.Mock()
    block._ctx = SimpleNamespace(is_disable_mouse_click_events=True)
    block._dispatch_mouse_action.return_value = True
    event = _release(button)

    VideoBlock.mouseReleaseEvent(block, event)

    assert block._dispatch_mouse_action.called is is_dispatched
    assert event.isAccepted() is is_dispatched


@pytest.mark.parametrize(
    ("sequence", "is_side"),
    [
        ("Back-Click", True),
        ("Ctrl+Forward-Click", True),
        ("Double Back-Click", True),
        ("Click-4", True),
        ("Click", False),
        ("Right-Click", False),
        ("Double Middle-Click", False),
        ("Wheel-Up", False),
        ("Ctrl+Middle-Drag", False),
    ],
)
def test_which_sequences_are_side_buttons(sequence, is_side):
    assert MouseButtonSequence(sequence).is_side_button is is_side
