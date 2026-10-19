"""Rotate to fit: a video turned on its side where its shape is the other
one to its cell's, a landscape video standing up in a tall cell and a
portrait one lying down in a wide cell.

One app-wide setting, "player/auto_rotate", off by default, and the way it
turns, "player/auto_rotate_direction": Rotate 90 (clockwise) or Rotate 270
(counter-clockwise), the same both ways round. The turn is the video's own
transform (Video.transform), the one the Transform menu sets, so crop,
screenshots and the crop dialog go by it the same as by a turn picked
there. Video.is_transform_auto says the transform there is this one's.

A transform picked by hand wins for the file it was picked for
(Video.transform_picked_for); the next file in the cell is turned to fit
again. A transform the video came with otherwise, from the video defaults
or a playlist saved before, is left as it is.
"""

from gridplayer.params.static import ROTATION_TRANSFORMS, VideoTransform

SETTING = "player/auto_rotate"
DIRECTION_SETTING = "player/auto_rotate_direction"

AUTO_TURNS = (VideoTransform.ROTATE_90, VideoTransform.ROTATE_270)
DEFAULT_TURN = VideoTransform.ROTATE_90

# a video or a cell within this of square has no shape to turn for
SQUARE_TOLERANCE = 0.05

PORTRAIT = "portrait"
LANDSCAPE = "landscape"
SQUARE = "square"


def shape_of(width: int, height: int) -> str | None:
    """PORTRAIT, LANDSCAPE or SQUARE (within SQUARE_TOLERANCE of it);
    None where the size is not known."""

    if not width or not height or width <= 0 or height <= 0:
        return None

    if max(width, height) / min(width, height) <= 1 + SQUARE_TOLERANCE:
        return SQUARE

    return PORTRAIT if height > width else LANDSCAPE


def displayed_size(
    video_dimensions: tuple[int, int], orientation: VideoTransform | None
) -> tuple[int, int]:
    """The video's size as it is shown before any transform of our own:
    on its side where the file says to show it so, as a phone tags it."""

    width, height = video_dimensions

    if orientation in ROTATION_TRANSFORMS:
        return height, width

    return width, height


def turn_direction(direction) -> VideoTransform:
    return direction if direction in AUTO_TURNS else DEFAULT_TURN


def is_turn_wanted(
    video_dimensions: tuple[int, int],
    orientation: VideoTransform | None,
    cell_size: tuple[int, int],
) -> bool | None:
    """Whether the video is the other shape to its cell; None where either
    shape is not known yet."""

    video = shape_of(*displayed_size(video_dimensions, orientation))
    cell = shape_of(*cell_size)

    if video is None or cell is None:
        return None

    if SQUARE in (video, cell):
        return False

    return video != cell


def auto_transform(
    *,
    is_enabled: bool,
    direction,
    video_dimensions: tuple[int, int],
    orientation: VideoTransform | None,
    cell_size: tuple[int, int],
    transform: VideoTransform,
    is_transform_auto: bool,
    picked_for: str | None,
    uri,
) -> VideoTransform | None:
    """The transform the video is to change to, None to leave it as it is."""

    if not is_enabled:
        # turned back, the setting switched off
        if is_transform_auto and transform != VideoTransform.NONE:
            return VideoTransform.NONE
        return None

    # picked by hand for this file
    if picked_for is not None and picked_for == str(uri):
        return None

    # from the video defaults or a playlist saved before, not picked here
    if (
        picked_for is None
        and not is_transform_auto
        and transform != VideoTransform.NONE
    ):
        return None

    is_wanted = is_turn_wanted(video_dimensions, orientation, cell_size)

    if is_wanted is None:
        return None

    wanted = turn_direction(direction) if is_wanted else VideoTransform.NONE

    if wanted == transform:
        return None

    return wanted
