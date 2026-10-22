"""Rotate to fit in Settings: the Player page's switch and its direction,
saved like the rest, and the cells told when either changes."""

from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QEvent, QSettings
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.dialogs import settings as settings_dialog
from gridplayer.dialogs.settings import SettingsDialog
from gridplayer.params.static import VideoTransform
from gridplayer.player.managers.settings import SettingsManager
from gridplayer.player.managers.video_blocks import VideoBlocksManager
from gridplayer.settings import Settings, _default_settings, _Settings
from gridplayer.utils import auto_rotate



@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def store(tmp_path, monkeypatch):
    store = _Settings.__new__(_Settings)
    store.settings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    monkeypatch.setattr(settings_dialog, "Settings", lambda: store)
    return store


@pytest.fixture
def make_dialog(store):
    made = []

    def _make():
        dialog = SettingsDialog(None)
        made.append(dialog)
        return dialog

    yield _make

    for dialog in made:
        dialog.close()
        dialog.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_on_the_player_page_off_by_default(make_dialog):
    dialog = make_dialog()

    assert dialog.playerAutoRotate.isChecked() is False
    assert dialog.playerAutoRotateDirection.currentData() == VideoTransform.ROTATE_90
    assert dialog.playerAutoRotateDirection.isEnabled() is False
    assert dialog.playerAutoRotate.parent() is dialog.page_general_player_contents
    assert dialog.settings_map[auto_rotate.SETTING] is dialog.playerAutoRotate
    assert (
        dialog.settings_map[auto_rotate.DIRECTION_SETTING]
        is dialog.playerAutoRotateDirection
    )


def test_both_choices_offered(make_dialog):
    combo = make_dialog().playerAutoRotateDirection
    choices = [combo.itemData(i) for i in range(combo.count())]
    assert choices == [VideoTransform.ROTATE_90, VideoTransform.ROTATE_270]


def test_saved_and_read_back(make_dialog, store):
    dialog = make_dialog()
    dialog.playerAutoRotate.setChecked(True)
    assert dialog.playerAutoRotateDirection.isEnabled() is True
    dialog.playerAutoRotateDirection.setCurrentIndex(
        dialog.playerAutoRotateDirection.findData(VideoTransform.ROTATE_270)
    )

    dialog.save_settings()

    assert store.get(auto_rotate.SETTING) is True
    assert store.get(auto_rotate.DIRECTION_SETTING) == VideoTransform.ROTATE_270

    again = make_dialog()
    assert again.playerAutoRotate.isChecked() is True
    assert again.playerAutoRotateDirection.currentData() == VideoTransform.ROTATE_270


def _settings_manager():
    parent = QWidget()
    ctx = SimpleNamespace(commands=SimpleNamespace(), grid_state=None)
    manager = SettingsManager(context=ctx, parent=parent)
    manager._keep_parent = parent
    return manager


@pytest.mark.parametrize(
    ("key", "value"),
    [
        (auto_rotate.SETTING, True),
        (auto_rotate.DIRECTION_SETTING, VideoTransform.ROTATE_270),
    ],
)
def test_the_cells_are_told_when_it_changes(mocker, key, value):
    manager = _settings_manager()
    changed = mocker.Mock()
    manager.auto_rotate_changed.connect(changed)
    current = dict(_default_settings)
    current[key] = value
    mocker.patch.object(Settings(), "get", side_effect=current.__getitem__)

    manager._apply_settings(dict(_default_settings))

    changed.assert_called_once_with()


def test_the_cells_are_not_told_when_it_does_not(mocker):
    manager = _settings_manager()
    changed = mocker.Mock()
    manager.auto_rotate_changed.connect(changed)
    mocker.patch.object(Settings(), "get", side_effect=_default_settings.__getitem__)

    manager._apply_settings(dict(_default_settings))

    changed.assert_not_called()


def test_toggle_switches_the_setting_and_every_cell_looks_again(mocker):
    values = dict(_default_settings)
    mocker.patch.object(Settings(), "get", side_effect=lambda k: values[k])
    mocker.patch.object(
        Settings(), "set", side_effect=lambda k, v: values.__setitem__(k, v)
    )

    block = SimpleNamespace(auto_rotate=mocker.Mock())
    manager = SimpleNamespace(
        _ctx=SimpleNamespace(is_auto_rotate=False, video_blocks=[block])
    )
    manager.apply_auto_rotate_settings = lambda: (
        VideoBlocksManager.apply_auto_rotate_settings(manager)
    )

    VideoBlocksManager.toggle_auto_rotate(manager)

    assert values[auto_rotate.SETTING] is True
    assert manager._ctx.is_auto_rotate is True
    assert manager._ctx.auto_rotate_direction == VideoTransform.ROTATE_90
    block.auto_rotate.check.assert_called_once_with()

    VideoBlocksManager.toggle_auto_rotate(manager)

    assert values[auto_rotate.SETTING] is False
    assert block.auto_rotate.check.call_count == 2


def test_the_action_has_no_default_key():
    from gridplayer.params.actions import ACTIONS

    action = ACTIONS["Rotate to Fit"]
    assert "key" not in action
    assert action["func"] == "toggle_auto_rotate"
    assert action["check_if"] == "is_auto_rotate"
