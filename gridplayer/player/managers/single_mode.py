from PyQt5.QtCore import pyqtSignal

from gridplayer.player.managers.base import ManagerBase
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.settings import Settings


class SingleModeManager(ManagerBase):
    mode_changed = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._ctx.is_single_mode = False
        self._ctx.is_pause_background_videos = Settings().get(
            "playlist/pause_background_videos"
        )

        self._pre_sm_states = {}

        # the video single mode shows; the active one as it was entered,
        # then the one it was switched to
        self._shown = None

    @property
    def commands(self):
        return {
            "next_single_video": self.next_single_video,
            "previous_single_video": self.previous_single_video,
            "toggle_single_video": self.toggle_single_video,
            "toggle_single_video_for": self.toggle_single_video_for,
            "is_single_mode": lambda: self._ctx.is_single_mode,
            "is_more_than_one_video": lambda: len(self._ctx.video_blocks) > 1,
            "is_single_mode_available": self.is_single_mode_available,
            "is_pause_background_videos": lambda: self._ctx.is_pause_background_videos,
            "set_pause_background_videos": self.set_pause_background_videos,
            "toggle_pause_background_videos": self.toggle_pause_background_videos,
        }

    def set_video_count(self, video_count):
        """Exit single mode when number of videos change"""

        if self._ctx.is_single_mode:
            self.single_mode_off()

    def is_single_mode_available(self):
        return (
            len(self._ctx.video_blocks) >= 1
            and self._ctx.commands.grid_cell_count() > 1
        )

    def set_pause_background_videos(self, is_pause):
        was_pause = self._ctx.is_pause_background_videos
        self._ctx.is_pause_background_videos = is_pause
        if not self._ctx.is_single_mode or was_pause == is_pause:
            return

        if is_pause:
            self._pause_hidden_videos()
        else:
            self._restore_hidden_videos()

    def toggle_pause_background_videos(self):
        value = not self._ctx.is_pause_background_videos
        PlaylistSettings().set("playlist/pause_background_videos", value)
        self.set_pause_background_videos(value)

    def _pause_hidden_videos(self):
        for vb in self._ctx.video_blocks:
            if vb is self._shown:
                continue
            self._pause_playing(vb)

    def _restore_hidden_videos(self):
        for vb in self._ctx.video_blocks:
            if vb is self._shown:
                continue
            self._restore_playing(vb)

    def toggle_single_video(self):
        if self._ctx.is_single_mode:
            self.single_mode_off()
            return

        if not self.is_single_mode_available():
            return

        self.single_mode_on()

    def toggle_single_video_for(self, vb):
        """Single mode on that video, or off if it is on already."""

        if self._ctx.is_single_mode:
            self.single_mode_off()
            return

        if not self.is_single_mode_available():
            return

        self.single_mode_on(vb)

    def next_single_video(self):
        self._switch_single_video(is_before=False)

    def previous_single_video(self):
        self._switch_single_video(is_before=True)

    def single_mode_on(self, vb=None):
        shown = vb if vb is not None else self._ctx.active_block
        if shown is None:
            return

        if shown is not self._ctx.active_block:
            self._ctx.commands.set_active_block(shown)

        self._ctx.is_single_mode = True
        self._shown = shown

        for vb in self._ctx.video_blocks:
            if vb is shown:
                continue

            self._pause_playing(vb)
            vb.hide()

        self.mode_changed.emit()

    def single_mode_off(self):
        self._ctx.is_single_mode = False

        # Whichever was shown last plays on as it is; every other one that
        # single mode paused plays again, the first one shown included when
        # it was switched away from. Those paused by the viewer stay paused.
        for vb in self._ctx.video_blocks:
            if vb is self._shown:
                continue

            self._restore_playing(vb)

        self._pre_sm_states.clear()
        self._shown = None

        # The grid shows the hidden videos as it lays them out again, all at
        # once. Shown here one by one, each would lay the grid out on the spot.
        self.mode_changed.emit()

    def _switch_single_video(self, is_before):
        if not self._ctx.is_single_mode:
            return

        current_sv = self._shown
        if current_sv is None or current_sv not in list(self._ctx.video_blocks):
            current_sv = next(v for v in self._ctx.video_blocks if v.isVisible())

        next_sv = self._find_next_single_video(current_sv, is_before)

        if next_sv is current_sv:
            return

        self._pause_playing(current_sv)
        current_sv.hide()

        self._restore_playing(next_sv)
        next_sv.show()
        self._shown = next_sv

        # the one shown is the one the keys are for (B/N, PgUp/PgDn, ...),
        # without waiting for the mouse to move over it
        self._ctx.commands.set_active_block(next_sv)

    def _find_next_single_video(self, current_sv, is_before):
        blocks = self._ctx.video_blocks.blocks_for_ids(
            self._ctx.commands.layout_order()
        )
        if not blocks:
            return current_sv
        idx = blocks.index(current_sv)
        if is_before:
            return blocks[idx - 1]
        return blocks[(idx + 1) % len(blocks)]

    def _pause_playing(self, vb):
        if not self._ctx.is_pause_background_videos:
            return
        # is_paused is only what VLC has confirmed. A cell still on its way
        # to playing would be left out, then play on while it is hidden.
        if vb.is_pause_wanted:
            return
        self._pre_sm_states[vb.id] = False
        vb.set_pause(True)

    def _restore_playing(self, vb):
        pre_sm_state = self._pre_sm_states.pop(vb.id, None)
        if pre_sm_state is not None:
            vb.set_pause(pre_sm_state)
