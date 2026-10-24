"""The wheel over a cell is that cell's volume: a step of the volume step
setting a notch, said over the video, in whole percents, never past 100%."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt5.QtCore import QEvent, QPoint, QSettings, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs import settings as settings_dialog
from gridplayer.dialogs.settings import SettingsDialog
from gridplayer.models.video import Video
from gridplayer.player.managers.actions import ActionsManager
from gridplayer.settings import Settings, _default_settings, _Settings
from gridplayer.utils import volume

from gridplayer.utils.keymap import WheelNotches, default_keymap, merge_keymap
from gridplayer.vlc_player.player_base import VlcPlayerBase
from gridplayer.widgets.video_block_audio import AudioControl
from gridplayer.widgets.video_overlay_elements import OverlayVolumeBar


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path):
    settings = Settings()
    settings.settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)


def _set_step(step):
    Settings().set(volume.STEP_SETTING, step)


def _block(volume_now=0.5, is_muted=False):
    """A cell heard at volume_now: a Video is muted to start with."""

    block = Mock()
    block.is_video_initialized = True
    block.video_params = Video(uri="http://example.com/a.mp4")
    block.video_params.volume = volume_now
    block.video_params.is_muted = is_muted
    block.audio = AudioControl(block)
    return block


def _sent(block):
    return block.video_driver.audio_set_volume.call_args.args[0]


# ---------------------------------------------------------------------------
# the keys


class TestTheDefaultKeys:
    def test_the_wheel_is_the_volume(self):
        defaults = default_keymap()

        assert defaults["Audio Volume - Increase"] == ["Wheel-Up"]
        assert defaults["Audio Volume - Decrease"] == ["Wheel-Down"]

    def test_and_no_longer_a_seek(self):
        defaults = default_keymap()

        assert defaults["+1%"] == ["Right"]
        assert defaults["-1%"] == ["Left"]
        assert defaults["+5%"] == []
        assert defaults["-5%"] == []

        for seek in ("+1%", "-1%", "+5%", "-5%"):
            assert not any("Wheel" in key for key in defaults[seek])

    def test_zoom_keeps_its_ctrl_wheel(self):
        defaults = default_keymap()

        assert "Ctrl+Wheel-Up" in defaults["Zoom In"]
        assert "Ctrl+Wheel-Down" in defaults["Zoom Out"]

    def test_the_volume_is_the_active_cells(self):
        from gridplayer.params.actions import ACTIONS

        assert ACTIONS["Audio Volume - Increase"]["func"] == (
            "active",
            "audio.volume_increase",
        )
        assert ACTIONS["Audio Volume - Decrease"]["func"] == (
            "active",
            "audio.volume_decrease",
        )

    def test_a_remap_of_ones_own_is_kept(self):
        keymap = merge_keymap(default_keymap(), {"+1%": ["Right", "Wheel-Down"]})

        assert keymap["+1%"] == ["Right", "Wheel-Down"]
        # the wheel is theirs for the seek, the volume lets it go
        assert "Wheel-Down" not in keymap["Audio Volume - Decrease"]
        assert keymap["Audio Volume - Increase"] == ["Wheel-Up"]


class TestTheWheelOverACell:
    @pytest.fixture
    def manager(self):
        manager = Mock()
        manager._ctx = SimpleNamespace(
            is_disable_mouse_click_events=False,
            is_disable_mouse_wheel_events=False,
            commands=SimpleNamespace(handle_fake_drag_click=lambda event: False),
        )
        manager._mouse_index = {
            "Wheel-Up": "Audio Volume - Increase",
            "Wheel-Down": "Audio Volume - Decrease",
        }
        manager._wheel_notches = WheelNotches()
        manager.trigger.return_value = True
        return manager

    @staticmethod
    def _wheel(dy, modifiers=Qt.NoModifier):
        event = QWheelEvent(
            QPoint(0, 0),
            QPoint(0, 0),
            QPoint(0, 0),
            QPoint(0, dy),
            0,
            Qt.Vertical,
            Qt.NoButton,
            modifiers,
        )
        event.setTimestamp(0)
        return event

    @pytest.mark.parametrize(
        ("dy", "action"),
        [(120, "Audio Volume - Increase"), (-120, "Audio Volume - Decrease")],
    )
    def test_a_notch_is_a_step(self, manager, dy, action):
        assert ActionsManager.handle_mouse_event(manager, self._wheel(dy))

        manager.trigger.assert_called_once_with(action)

    @pytest.mark.parametrize(("dy", "action"), [(120, "Zoom In"), (-120, "Zoom Out")])
    def test_ctrl_wheel_is_still_the_zoom(self, manager, dy, action):
        manager._mouse_index.update(
            {"Ctrl+Wheel-Up": "Zoom In", "Ctrl+Wheel-Down": "Zoom Out"}
        )

        assert ActionsManager.handle_mouse_event(
            manager, self._wheel(dy, Qt.ControlModifier)
        )

        manager.trigger.assert_called_once_with(action)

    @pytest.mark.parametrize("modifiers", [Qt.NoModifier, Qt.ControlModifier])
    def test_disable_mouse_wheel_events_blocks_it(self, manager, modifiers):
        manager._ctx.is_disable_mouse_wheel_events = True
        manager._mouse_index.update({"Ctrl+Wheel-Up": "Zoom In"})

        assert not ActionsManager.handle_mouse_event(
            manager, self._wheel(120, modifiers)
        )

        manager.trigger.assert_not_called()

    def test_the_cell_lets_it_go_when_wheel_events_are_disabled(self):
        from gridplayer.widgets.video_block import VideoBlock

        block = SimpleNamespace(
            _ctx=SimpleNamespace(is_disable_mouse_wheel_events=True),
            _dispatch_mouse_action=Mock(return_value=True),
        )
        event = self._wheel(120)

        VideoBlock.wheelEvent(block, event)

        block._dispatch_mouse_action.assert_not_called()
        assert not event.isAccepted()


# ---------------------------------------------------------------------------
# the step


class TestTheStep:
    def test_five_by_default(self):
        assert _default_settings[volume.STEP_SETTING] == 5
        assert volume.volume_step() == 5

    @pytest.mark.parametrize(("step", "up", "down"), [(1, 0.51, 0.49), (5, 0.55, 0.45)])
    def test_the_setting_is_the_step(self, step, up, down):
        _set_step(step)

        block = _block(0.5)
        block.audio.volume_increase()
        assert block.video_params.volume == up

        block = _block(0.5)
        block.audio.volume_decrease()
        assert block.video_params.volume == down

    @pytest.mark.parametrize(("stored", "used"), [(0, 1), (99, 25), (12, 12)])
    def test_kept_between_1_and_25(self, stored, used):
        _set_step(stored)

        assert volume.volume_step() == used

    def test_one_percent_lands_on_every_percent(self):
        _set_step(1)
        block = _block(0.16)

        block.audio.volume_increase()
        assert block.video_params.volume == 0.17
        assert _sent(block) == 0.17

        block.audio.volume_increase()
        assert block.video_params.volume == 0.18

    def test_a_hundred_steps_do_not_drift(self):
        _set_step(1)
        block = _block(0.0)

        for percent in range(1, 101):
            block.audio.volume_increase()
            assert round(block.video_params.volume * 100, 6) == percent

        for percent in range(99, -1, -1):
            block.audio.volume_decrease()
            assert round(block.video_params.volume * 100, 6) == percent

    def test_a_step_unmutes(self):
        block = _block(0.5)
        block.video_params.is_muted = True

        block.audio.volume_increase()

        assert block.video_params.is_muted is False


# ---------------------------------------------------------------------------
# a notch from the wheel to the cell, one step for each


def _wheel_event(dy, ms=0):
    event = QWheelEvent(
        QPoint(0, 0),
        QPoint(0, 0),
        QPoint(0, 0),
        QPoint(0, dy),
        0,
        Qt.Vertical,
        Qt.NoButton,
        Qt.NoModifier,
    )
    event.setTimestamp(ms)
    return event


class TestOneNotchOneStep:
    """The maintainer's report: one notch of the wheel took a cell to 100%."""

    @pytest.fixture
    def wheel(self):
        """A cell, and the wheel turned over it as the player takes it."""

        def _make(volume_now, is_muted=False):
            block = _block(volume_now, is_muted)

            funcs = {
                "Audio Volume - Increase": block.audio.volume_increase,
                "Audio Volume - Decrease": block.audio.volume_decrease,
            }

            manager = Mock()
            manager._ctx = SimpleNamespace(
                is_disable_mouse_click_events=False,
                is_disable_mouse_wheel_events=False,
                commands=SimpleNamespace(handle_fake_drag_click=lambda event: False),
            )
            manager._mouse_index = {
                "Wheel-Up": "Audio Volume - Increase",
                "Wheel-Down": "Audio Volume - Decrease",
            }
            manager._wheel_notches = WheelNotches()
            manager.trigger.side_effect = lambda action_id: funcs[action_id]()

            def turn(dy, ms=0):
                return ActionsManager.handle_mouse_event(manager, _wheel_event(dy, ms))

            return block, turn

        return _make

    @pytest.mark.parametrize(
        ("step", "dy", "after"),
        [(1, 120, 0.51), (1, -120, 0.49), (5, 120, 0.55), (5, -120, 0.45)],
    )
    def test_a_notch_at_50(self, wheel, step, dy, after):
        _set_step(step)
        block, turn = wheel(0.5)

        assert turn(dy)

        assert block.video_params.volume == after
        assert _sent(block) == after
        block.info_change.emit.assert_called_once_with(f"Volume {round(after * 100)}%")

    @pytest.mark.parametrize("step", [1, 5])
    def test_fine_turns_add_up_to_one_step(self, wheel, step):
        """A touchpad or a smooth wheel: 8 turns of 15 are one notch."""

        _set_step(step)
        block, turn = wheel(0.5)

        for i in range(7):
            turn(15, ms=i * 10)
            assert block.video_params.volume == 0.5

        turn(15, ms=70)
        assert round(block.video_params.volume * 100) == 50 + step

        for i in range(8, 16):
            turn(15, ms=i * 10)
        assert round(block.video_params.volume * 100) == 50 + 2 * step

    @pytest.mark.parametrize("step", [1, 5])
    def test_a_new_cell_starts_muted_at_100_and_ramps_up_from_0(self, wheel, step):
        """A new cell is muted at the default volume, 100%: unmuting it at
        that on the first notch was the jump to 100%."""

        assert _default_settings["video_defaults/muted"] is True
        assert _default_settings["video_defaults/volume"] == 1.0

        _set_step(step)
        block, turn = wheel(1.0, is_muted=True)

        turn(120)

        assert block.video_params.is_muted is False
        assert round(block.video_params.volume * 100) == step
        assert _sent(block) == step / 100
        block.info_change.emit.assert_called_once_with(f"Volume {step}%")

        turn(120, ms=10)
        assert round(block.video_params.volume * 100) == 2 * step

    def test_turned_down_while_muted_it_stays_muted(self, wheel):
        _set_step(5)
        block, turn = wheel(0.8, is_muted=True)

        turn(-120)

        assert block.video_params.is_muted is True
        assert block.video_params.volume == 0.8
        block.video_driver.audio_set_volume.assert_not_called()
        block.info_change.emit.assert_called_once_with("Volume 0%")

    def test_a_key_press_from_mute_is_one_step_too(self):
        _set_step(1)
        block = _block(1.0, is_muted=True)

        block.audio.volume_increase()

        assert block.video_params.volume == 0.01
        assert block.video_params.is_muted is False


# ---------------------------------------------------------------------------
# the cap and the floor


class TestNeverPast100:
    @pytest.mark.parametrize("asked", [1.0, 1.01, 1.3, 25])
    def test_set_volume(self, asked):
        block = _block()

        block.audio.set_volume(asked)

        assert block.video_params.volume == 1.0
        assert _sent(block) == 1.0
        block.volume_change.emit.assert_called_with(1.0)

    @pytest.mark.parametrize("asked", [-0.01, -5, None, float("nan")])
    def test_or_under_0(self, asked):
        block = _block()

        block.audio.set_volume(asked)

        assert block.video_params.volume == 0.0
        assert _sent(block) == 0.0

    @pytest.mark.parametrize("step", [1, 5, 25])
    def test_the_steps_stop_at_100(self, step):
        _set_step(step)
        block = _block(0.98)

        for _ in range(5):
            block.audio.volume_increase()

        assert block.video_params.volume == 1.0
        assert _sent(block) == 1.0

    @pytest.mark.parametrize("step", [1, 5, 25])
    def test_and_at_0(self, step):
        _set_step(step)
        block = _block(0.02)

        for _ in range(5):
            block.audio.volume_decrease()

        assert block.video_params.volume == 0.0
        assert _sent(block) == 0.0

    def test_a_playlist_or_the_defaults_past_100(self):
        """A loaded video's own volume goes through set_volume too."""

        block = _block(1.3)

        block.audio.set_volume(block.video_params.volume)

        assert block.video_params.volume == 1.0

    @pytest.mark.parametrize(
        ("y", "position"), [(-50, 1.0), (0, 1.0), (50, 0.5), (100, 0.0), (150, 0.0)]
    )
    def test_the_slider(self, y, position):
        bar = SimpleNamespace(
            progress_select_y=None, height=lambda: 100, position_changed=Mock()
        )

        OverlayVolumeBar._update_position(bar, y)

        bar.position_changed.emit.assert_called_once_with(position)


class TestWhatVlcIsTold:
    @pytest.fixture
    def player(self):
        return SimpleNamespace(_media_player=Mock())

    @pytest.mark.parametrize(
        ("volume_now", "told"),
        [(0.29, 29), (0.57, 57), (0.17, 17), (0.01, 1), (1.0, 100)],
    )
    def test_rounded_not_cut_short(self, player, volume_now, told):
        VlcPlayerBase.audio_set_volume(player, volume_now)

        player._media_player.audio_set_volume.assert_called_once_with(told)

    @pytest.mark.parametrize(("volume_now", "told"), [(1.3, 100), (-0.2, 0)])
    def test_never_past_100_or_under_0(self, player, volume_now, told):
        VlcPlayerBase.audio_set_volume(player, volume_now)

        player._media_player.audio_set_volume.assert_called_once_with(told)

    def test_every_percent_is_itself(self):
        for percent in range(101):
            assert volume.volume_percent(percent / 100) == percent


# ---------------------------------------------------------------------------
# what the cell says


class TestWhatTheCellSays:
    def test_the_text(self):
        assert volume.volume_txt(0.17) == "Volume 17%"
        assert volume.volume_txt(1.0) == "Volume 100%"
        assert volume.volume_txt(0) == "Volume 0%"

    def test_said_on_a_step_up(self):
        _set_step(1)
        block = _block(0.16)

        block.audio.volume_increase()

        block.info_change.emit.assert_called_once_with("Volume 17%")

    def test_said_on_a_step_down(self):
        block = _block(0.5)

        block.audio.volume_decrease()

        block.info_change.emit.assert_called_once_with("Volume 45%")

    def test_said_at_the_cap(self):
        block = _block(1.0)

        block.audio.volume_increase()

        block.info_change.emit.assert_called_once_with("Volume 100%")

    def test_the_slider_says_nothing(self):
        block = _block(0.5)

        block.audio.set_volume(0.3)

        block.info_change.emit.assert_not_called()


# ---------------------------------------------------------------------------
# Settings


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


class TestInSettings:
    def test_on_the_player_page(self, make_dialog):
        dialog = make_dialog()
        box = dialog.widget(volume.STEP_SETTING)

        assert box.value() == 5
        assert (box.minimum(), box.maximum()) == (1, 25)
        assert box.isEnabled()
        assert dialog.pages["player"].isAncestorOf(box)

    def test_saved_and_read_back(self, make_dialog, store):
        dialog = make_dialog()
        dialog.widget(volume.STEP_SETTING).setValue(1)
        dialog.save_settings()

        assert store.get(volume.STEP_SETTING) == 1

        again = make_dialog()
        assert again.widget(volume.STEP_SETTING).value() == 1

    def test_whole_numbers_only(self, make_dialog):
        box = make_dialog().widget(volume.STEP_SETTING)

        box.setValue(30)
        assert box.value() == 25
        box.setValue(0)
        assert box.value() == 1
