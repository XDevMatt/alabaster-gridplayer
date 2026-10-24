"""Rotate to fit for one cell: its video turned on its side where it is the
other shape to the cell, as gridplayer.utils.auto_rotate decides.

Looked at once a file has loaded in the cell (a Next, a Previous, a random
or a shuffled file included, which load the same way), once the cell has
settled on a new shape (the grid laid out again, the window resized), and
when the setting is changed. A turn is the video's transform, which VLC
only takes on opening it, so turning it is opening it again.
"""

import logging

from PyQt5.QtCore import QTimer

from gridplayer.params.static import NO_CROP_RATIO, VideoTransform, is_crop_unpicked
from gridplayer.utils.auto_rotate import (
    auto_transform,
    is_turn_wanted,
    turn_direction,
)
from gridplayer.widgets.video_block_guards import VideoBlockPart

# a cell being resized is looked at once it has stopped changing
RESIZE_SETTLE_MS = 400

# a video whose size VLC has not said yet is looked at again, this often,
# this many times
SIZE_RETRY_MS = 500
SIZE_RETRIES = 10

# turns of one file in one shape of cell before it is left as it is, in case
# the size VLC gives changes with the turn
MAX_TURNS_PER_SHAPE = 2

_log = logging.getLogger(__name__)


class AutoRotateControl(VideoBlockPart):
    def __init__(self, block):
        super().__init__(block)

        self._resize_timer = QTimer(block)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(RESIZE_SETTLE_MS)
        self._resize_timer.timeout.connect(self.check)

        self._size_timer = QTimer(block)
        self._size_timer.setSingleShot(True)
        self._size_timer.setInterval(SIZE_RETRY_MS)
        self._size_timer.timeout.connect(self._check_size_again)
        self._size_retries = 0

        # (uri, cell shape) -> times turned, for the file in the cell now
        self._turns: dict = {}

    @property
    def is_enabled(self) -> bool:
        return bool(getattr(self._block._ctx, "is_auto_rotate", False))

    @property
    def direction(self) -> VideoTransform:
        return turn_direction(getattr(self._block._ctx, "auto_rotate_direction", None))

    def on_loaded(self):
        self._size_retries = 0
        self.check()

    def on_resized(self):
        params = self._block.video_params
        if params is None:
            return

        if self.is_enabled or params.is_transform_auto:
            self._resize_timer.start()

    def on_picked(self):
        """A transform picked by hand: the one this file keeps."""

        params = self._block.video_params
        params.transform_picked_for = str(params.uri)
        params.is_transform_auto = False

    def stop(self):
        self._resize_timer.stop()
        self._size_timer.stop()

    def _check_size_again(self):
        self._size_retries += 1
        self.check()

    def check(self):
        block = self._block
        params = block.video_params

        if params is None or block.is_closing or not block.is_video_initialized:
            return

        media = getattr(block.video_driver, "media", None)
        track = media.cur_video_track if media is not None else None
        if track is None:
            return

        cell_size = (block.width(), block.height())
        is_enabled = self.is_enabled
        sar = getattr(track, "sar", None)
        is_shape_picked = _is_shape_picked(block)

        new = auto_transform(
            is_enabled=is_enabled,
            direction=self.direction,
            video_dimensions=track.video_dimensions,
            orientation=track.orientation,
            cell_size=cell_size,
            transform=params.transform,
            is_transform_auto=params.is_transform_auto,
            picked_for=params.transform_picked_for,
            uri=params.uri,
            sar=sar,
            is_shape_picked=is_shape_picked,
        )

        is_wanted = is_turn_wanted(
            track.video_dimensions,
            track.orientation,
            cell_size,
            sar,
            is_shape_picked,
        )

        if new is None:
            if is_enabled and is_wanted is None and not all(track.video_dimensions):
                # the size of it not known yet, maybe later
                if self._size_retries < SIZE_RETRIES:
                    self._size_timer.start()
                return

            # a pick for another file, the transform already the one it
            # would be turned to: the turn's from now on
            if (
                is_enabled
                and is_wanted is not None
                and params.transform_picked_for not in (None, str(params.uri))
                and params.transform in (VideoTransform.NONE, self.direction)
            ):
                params.transform_picked_for = None
                params.is_transform_auto = params.transform != VideoTransform.NONE
            return

        key = (str(params.uri), is_wanted)
        if key[0] not in {k[0] for k in self._turns}:
            self._turns = {}
        turns = self._turns.get(key, 0)
        if turns >= MAX_TURNS_PER_SHAPE:
            _log.warning(f"Rotate to fit: {params.uri_name} left as it is")
            return
        self._turns[key] = turns + 1

        _log.debug(f"Rotate to fit: {params.uri_name} {params.transform} -> {new}")

        params.transform = new
        params.is_transform_auto = new != VideoTransform.NONE
        params.transform_picked_for = None

        block.reload()


def _is_shape_picked(block) -> bool:
    """An aspect ratio or a crop shape the video is shown in, picked for it
    or its channel list's (upstream's Aspect Ratio and Crop menus)."""

    if getattr(block, "shown_aspect_ratio", ""):
        return True

    params = block.video_params
    crop_ratio = getattr(params, "crop_ratio", "")

    if crop_ratio and crop_ratio != NO_CROP_RATIO:
        return True

    # a list's shape counts only where no shape and no margins are picked
    return is_crop_unpicked(crop_ratio, getattr(params, "crop", ())) and bool(
        getattr(block, "list_crop_ratio", "")
    )
