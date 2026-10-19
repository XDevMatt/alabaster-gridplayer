"""Rotate to fit: which way, if at all, a cell turns its video."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gridplayer.models.video import Video
from gridplayer.params.static import VideoTransform
from gridplayer.settings import _default_settings
from gridplayer.utils import auto_rotate
from gridplayer.utils.auto_rotate import (
    auto_transform,
    displayed_size,
    is_turn_wanted,
    shape_of,
)
from gridplayer.widgets.video_block_auto_rotate import AutoRotateControl

NONE = VideoTransform.NONE
R90 = VideoTransform.ROTATE_90
R270 = VideoTransform.ROTATE_270

LANDSCAPE = (1920, 1080)
PORTRAIT = (1080, 1920)
TALL_CELL = (640, 1080)
WIDE_CELL = (960, 540)

URI = "C:/videos/clip.mp4"


def decide(
    video=LANDSCAPE,
    cell=TALL_CELL,
    *,
    is_enabled=True,
    direction=R90,
    orientation=NONE,
    transform=NONE,
    is_transform_auto=False,
    picked_for=None,
    uri=URI,
):
    return auto_transform(
        is_enabled=is_enabled,
        direction=direction,
        video_dimensions=video,
        orientation=orientation,
        cell_size=cell,
        transform=transform,
        is_transform_auto=is_transform_auto,
        picked_for=picked_for,
        uri=uri,
    )


def test_off_by_default():
    assert _default_settings[auto_rotate.SETTING] is False
    assert _default_settings[auto_rotate.DIRECTION_SETTING] == R90


def test_shapes():
    assert shape_of(1920, 1080) == auto_rotate.LANDSCAPE
    assert shape_of(1080, 1920) == auto_rotate.PORTRAIT
    assert shape_of(1000, 1000) == auto_rotate.SQUARE
    assert shape_of(1040, 1000) == auto_rotate.SQUARE
    assert shape_of(1000, 1049) == auto_rotate.SQUARE
    assert shape_of(1000, 1060) == auto_rotate.PORTRAIT
    assert shape_of(0, 0) is None
    assert shape_of(1920, 0) is None


@pytest.mark.parametrize("direction", [R90, R270])
def test_landscape_in_tall_cell_stands_up(direction):
    assert decide(LANDSCAPE, TALL_CELL, direction=direction) == direction


@pytest.mark.parametrize("direction", [R90, R270])
def test_portrait_in_wide_cell_lies_down(direction):
    assert decide(PORTRAIT, WIDE_CELL, direction=direction) == direction


@pytest.mark.parametrize(
    ("video", "cell"), [(LANDSCAPE, WIDE_CELL), (PORTRAIT, TALL_CELL)]
)
def test_matching_shapes_do_not_turn(video, cell):
    assert decide(video, cell) is None


@pytest.mark.parametrize(
    ("video", "cell"),
    [
        ((1000, 1000), TALL_CELL),
        ((1040, 1000), TALL_CELL),
        (LANDSCAPE, (1000, 1030)),
        (PORTRAIT, (1000, 1000)),
    ],
)
def test_near_square_does_not_turn(video, cell):
    assert decide(video, cell) is None


def test_near_square_turns_back_an_auto_turn():
    # the cell gone square: the turn it was given is taken off
    assert (
        decide(LANDSCAPE, (1000, 1000), transform=R90, is_transform_auto=True) == NONE
    )


def test_unknown_sizes_wait():
    assert decide((0, 0), TALL_CELL) is None
    assert decide(LANDSCAPE, (0, 0)) is None
    assert decide(LANDSCAPE, (0, 0), transform=R90, is_transform_auto=True) is None


@pytest.mark.parametrize(
    "orientation",
    [
        VideoTransform.ROTATE_90,
        VideoTransform.ROTATE_270,
        VideoTransform.TRANSPOSE,
        VideoTransform.ANTITRANSPOSE,
    ],
)
def test_metadata_rotated_file_goes_by_its_displayed_shape(orientation):
    # stored 1920x1080, tagged to be shown on its side: a portrait video
    assert displayed_size(LANDSCAPE, orientation) == PORTRAIT
    assert decide(LANDSCAPE, TALL_CELL, orientation=orientation) is None
    assert decide(LANDSCAPE, WIDE_CELL, orientation=orientation) == R90


@pytest.mark.parametrize(
    "orientation",
    [VideoTransform.ROTATE_180, VideoTransform.HFLIP, VideoTransform.VFLIP],
)
def test_metadata_upside_down_or_flipped_keeps_its_shape(orientation):
    assert displayed_size(LANDSCAPE, orientation) == LANDSCAPE
    assert decide(LANDSCAPE, TALL_CELL, orientation=orientation) == R90


def test_setting_off_never_turns():
    for video in (LANDSCAPE, PORTRAIT):
        for cell in (TALL_CELL, WIDE_CELL):
            assert decide(video, cell, is_enabled=False) is None


def test_setting_off_turns_back_its_own_turn_only():
    assert decide(is_enabled=False, transform=R90, is_transform_auto=True) == NONE
    # one picked by hand stays
    assert decide(is_enabled=False, transform=R90, picked_for=URI) is None
    assert decide(is_enabled=False, transform=R90) is None


def test_auto_turn_kept_while_it_fits():
    assert decide(transform=R90, is_transform_auto=True) is None


def test_auto_turn_taken_off_when_the_cell_changes_shape():
    assert decide(LANDSCAPE, WIDE_CELL, transform=R90, is_transform_auto=True) == NONE


def test_next_file_of_the_matching_shape_turns_back():
    # the turn of the file before, the new one already fits
    assert decide(PORTRAIT, TALL_CELL, transform=R90, is_transform_auto=True) == NONE


@pytest.mark.parametrize(("old", "new"), [(R90, R270), (R270, R90)])
def test_direction_change_reapplies(old, new):
    assert decide(direction=new, transform=old, is_transform_auto=True) == new


@pytest.mark.parametrize(
    "picked",
    [NONE, R90, VideoTransform.ROTATE_180, VideoTransform.HFLIP, R270],
)
def test_manual_transform_wins_for_its_file(picked):
    assert decide(transform=picked, picked_for=URI) is None
    assert decide(PORTRAIT, TALL_CELL, transform=picked, picked_for=URI) is None


def test_manual_transform_lapses_on_the_next_file():
    other = "C:/videos/other.mp4"
    assert decide(transform=VideoTransform.HFLIP, picked_for=other) == R90
    assert decide(PORTRAIT, TALL_CELL, transform=R90, picked_for=other) == NONE


def test_transform_from_defaults_is_left_alone():
    # not picked here and not the turn's: the video defaults' or an old playlist's
    assert decide(transform=VideoTransform.ROTATE_180) is None
    assert decide(PORTRAIT, TALL_CELL, transform=R90) is None


def test_unknown_direction_falls_back_to_90():
    assert decide(direction=None) == R90
    assert decide(direction=VideoTransform.HFLIP) == R90


def test_is_turn_wanted():
    assert is_turn_wanted(LANDSCAPE, NONE, TALL_CELL) is True
    assert is_turn_wanted(LANDSCAPE, NONE, WIDE_CELL) is False
    assert is_turn_wanted((0, 0), NONE, WIDE_CELL) is None


def test_video_keeps_its_auto_flags_in_a_playlist(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"")
    video = Video(uri=f, transform=R90, is_transform_auto=True)
    back = Video.model_validate_json(video.model_dump_json())
    assert back.is_transform_auto is True
    assert back.transform_picked_for is None

    picked = Video(uri=f, transform=R270, transform_picked_for=str(f))
    back = Video.model_validate_json(picked.model_dump_json())
    assert back.transform_picked_for == str(f)
    assert back.is_transform_auto is False


# --- the cell's part -------------------------------------------------------


class _Block:
    """A cell, as much of one as AutoRotateControl asks about."""

    def __init__(self, video, cell, *, is_on=True, direction=R90, params=None):
        self._ctx = SimpleNamespace(
            is_auto_rotate=is_on, auto_rotate_direction=direction
        )
        track = SimpleNamespace(video_dimensions=video, orientation=NONE)
        self.video_driver = SimpleNamespace(
            media=SimpleNamespace(cur_video_track=track)
        )
        self.video_params = params or SimpleNamespace(
            uri=URI,
            uri_name="clip.mp4",
            transform=NONE,
            is_transform_auto=False,
            transform_picked_for=None,
        )
        self.is_closing = False
        self.is_video_initialized = True
        self.reload = Mock()
        self._cell = cell

    def width(self):
        return self._cell[0]

    def height(self):
        return self._cell[1]


def _control(block):
    control = AutoRotateControl.__new__(AutoRotateControl)
    control._block = block
    control._size_retries = 0
    control._turns = {}
    control._size_timer = Mock()
    control._resize_timer = Mock()
    return control


@pytest.mark.parametrize("direction", [R90, R270])
def test_control_turns_and_reloads(direction):
    block = _Block(LANDSCAPE, TALL_CELL, direction=direction)
    _control(block).check()
    assert block.video_params.transform == direction
    assert block.video_params.is_transform_auto is True
    block.reload.assert_called_once()


def test_control_off_leaves_the_cell_alone():
    block = _Block(LANDSCAPE, TALL_CELL, is_on=False)
    _control(block).check()
    assert block.video_params.transform == NONE
    block.reload.assert_not_called()


def test_control_manual_pick_wins():
    block = _Block(LANDSCAPE, TALL_CELL)
    control = _control(block)
    block.video_params.transform = VideoTransform.ROTATE_180
    control.on_picked()
    control.check()
    assert block.video_params.transform == VideoTransform.ROTATE_180
    assert block.video_params.transform_picked_for == URI
    block.reload.assert_not_called()


def test_control_stops_turning_a_file_that_keeps_asking():
    block = _Block(LANDSCAPE, TALL_CELL)
    control = _control(block)
    for _ in range(5):
        block.video_params.transform = NONE
        block.video_params.is_transform_auto = False
        control.check()
    assert block.reload.call_count == 2


def test_control_waits_for_the_size():
    block = _Block((0, 0), TALL_CELL)
    control = _control(block)
    control.check()
    control._size_timer.start.assert_called_once()
    block.reload.assert_not_called()


def test_control_lapsed_pick_adopted_when_it_already_fits():
    block = _Block(LANDSCAPE, TALL_CELL)
    block.video_params.transform = R90
    block.video_params.transform_picked_for = "C:/videos/before.mp4"
    _control(block).check()
    assert block.video_params.is_transform_auto is True
    assert block.video_params.transform_picked_for is None
    block.reload.assert_not_called()


def test_resize_only_looked_at_with_the_setting_on_or_a_turn():
    block = _Block(LANDSCAPE, TALL_CELL, is_on=False)
    control = _control(block)
    control.on_resized()
    control._resize_timer.start.assert_not_called()
    block.video_params.is_transform_auto = True
    control.on_resized()
    control._resize_timer.start.assert_called_once()
