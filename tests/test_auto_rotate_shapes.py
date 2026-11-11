"""Rotate to fit and the aspect (orientation) filter, reconciled with
upstream's pixel shapes, Aspect Ratio and Crop (merge of 2026-10-23).

A video is the shape upstream shows it in: its pixels as wide as its SAR
says. A shape picked for it (an aspect ratio, a crop shape, or its list's)
is the shape it is shown in however it is turned, so it is not turned."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gridplayer.params.static import NO_CROP_RATIO, VideoCrop, VideoTransform
from gridplayer.utils import media_shape
from gridplayer.utils.auto_rotate import auto_transform, displayed_size, is_turn_wanted
from gridplayer.widgets.video_block_auto_rotate import (
    AutoRotateControl,
    _is_shape_picked,
)

NONE = VideoTransform.NONE
R90 = VideoTransform.ROTATE_90

TALL_CELL = (640, 1080)
WIDE_CELL = (960, 540)

# stored 320x360, shown 640x360: upstream's shapes/wide_pixels.mp4
WIDE_PIXELS = (320, 360)
SAR_2_1 = (2, 1)


def test_the_sar_widens_the_picture():
    assert displayed_size(WIDE_PIXELS, NONE, SAR_2_1) == (640, 360)
    assert displayed_size(WIDE_PIXELS, NONE) == (320, 360)


def test_the_sar_is_applied_before_the_file_turns_it():
    assert displayed_size(WIDE_PIXELS, R90, SAR_2_1) == (360, 640)


def test_a_wide_pixel_video_is_landscape_and_stands_up_in_a_tall_cell():
    assert is_turn_wanted(WIDE_PIXELS, NONE, TALL_CELL, SAR_2_1) is True
    assert is_turn_wanted(WIDE_PIXELS, NONE, WIDE_CELL, SAR_2_1) is False


def test_a_dvb_picture_is_landscape():
    # 720x576 shown 16:9
    assert is_turn_wanted((720, 576), NONE, TALL_CELL, (64, 45)) is True


@pytest.mark.parametrize("sar", [None, (0, 0), (1, 0)])
def test_no_sar_is_square_pixels(sar):
    assert displayed_size((1920, 1080), NONE, sar) == (1920, 1080)


def test_a_picked_shape_is_never_turned_for():
    assert is_turn_wanted((1920, 1080), NONE, TALL_CELL, is_shape_picked=True) is False


def _decide(**kwargs):
    defaults = {
        "is_enabled": True,
        "direction": R90,
        "video_dimensions": (1920, 1080),
        "orientation": NONE,
        "cell_size": TALL_CELL,
        "transform": NONE,
        "is_transform_auto": False,
        "picked_for": None,
        "uri": "clip.mp4",
    }
    defaults.update(kwargs)
    return auto_transform(**defaults)


def test_an_auto_turn_is_taken_back_once_a_shape_is_picked():
    assert _decide(transform=R90, is_transform_auto=True, is_shape_picked=True) == NONE


def test_nothing_is_turned_with_a_shape_picked():
    assert _decide(is_shape_picked=True) is None


def _block(*, aspect="", crop_ratio="", crop=None, list_crop=""):
    if crop is None:
        crop = VideoCrop(0, 0, 0, 0)
    return SimpleNamespace(
        shown_aspect_ratio=aspect,
        list_crop_ratio=list_crop,
        video_params=SimpleNamespace(crop_ratio=crop_ratio, crop=crop),
    )


@pytest.mark.parametrize(
    ("block", "picked"),
    [
        (_block(), False),
        (_block(aspect="16:9"), True),
        (_block(crop_ratio="2.35:1"), True),
        (_block(crop_ratio=NO_CROP_RATIO), False),
        (_block(list_crop="4:3"), True),
        (_block(list_crop="4:3", crop=VideoCrop(10, 0, 0, 0)), False),
        (_block(list_crop="4:3", crop_ratio=NO_CROP_RATIO), False),
    ],
)
def test_what_counts_as_a_picked_shape(block, picked):
    assert _is_shape_picked(block) is picked


def test_the_control_hands_over_the_sar_and_the_picked_shape():
    track = SimpleNamespace(video_dimensions=WIDE_PIXELS, orientation=NONE, sar=SAR_2_1)
    params = SimpleNamespace(
        uri="clip.mp4",
        uri_name="clip.mp4",
        transform=NONE,
        is_transform_auto=False,
        transform_picked_for=None,
        crop_ratio="",
        crop=VideoCrop(0, 0, 0, 0),
    )
    block = SimpleNamespace(
        _ctx=SimpleNamespace(is_auto_rotate=True, auto_rotate_direction=R90),
        video_driver=SimpleNamespace(media=SimpleNamespace(cur_video_track=track)),
        video_params=params,
        is_closing=False,
        is_video_initialized=True,
        reload=Mock(),
        shown_aspect_ratio="",
        list_crop_ratio="",
        width=lambda: TALL_CELL[0],
        height=lambda: TALL_CELL[1],
    )
    control = AutoRotateControl.__new__(AutoRotateControl)
    control._block = block
    control._size_retries = 0
    control._turns = {}
    control._size_timer = Mock()
    control._resize_timer = Mock()

    control.check()

    assert params.transform == R90
    block.reload.assert_called_once()

    # an aspect ratio picked: turned back
    block.shown_aspect_ratio = "16:9"
    block.reload.reset_mock()
    control.check()

    assert params.transform == NONE
    block.reload.assert_called_once()


def test_the_orientation_filter_goes_by_the_shown_shape_too():
    assert media_shape.is_portrait(320, 360) is True
    assert media_shape.is_portrait(320, 360, 0, SAR_2_1) is False
    assert media_shape.is_portrait(320, 360, 6, SAR_2_1) is True
