"""A cell's volume: kept in whole percents, never past 100% (VLC itself goes
to 125%), and stepped by the player/volume_step setting.

No Qt imported at the top: the VLC player processes use this too.
"""

STEP_SETTING = "player/volume_step"

MIN_STEP = 1
MAX_STEP = 25
DEFAULT_STEP = 5


def clamp_volume(volume) -> float:
    """0.0 to 1.0 in whole percents, whatever it was given."""

    try:
        volume = float(volume)
    except (TypeError, ValueError):
        return 0.0

    if volume != volume:  # NaN
        return 0.0

    return round(min(max(volume, 0.0), 1.0), 2)


def volume_percent(volume) -> int:
    """As VLC takes it, 0 to 100, rounded rather than cut short."""

    return round(clamp_volume(volume) * 100)


def clamp_step(step) -> int:
    try:
        step = int(step)
    except (TypeError, ValueError):
        return DEFAULT_STEP

    return min(max(step, MIN_STEP), MAX_STEP)


def volume_step() -> int:
    """The setting, in percent."""

    from gridplayer.settings import Settings

    return clamp_step(Settings().get(STEP_SETTING))


def stepped_volume(volume, step_percent: int, direction: int) -> float:
    """One step up (direction 1) or down (-1), counted in whole percents so
    steps of 1% land on every percent."""

    percent = volume_percent(volume) + direction * clamp_step(step_percent)

    return clamp_volume(percent / 100)


def volume_txt(volume) -> str:
    """What the cell says as its volume changes: "Volume 17%"."""

    from gridplayer.utils.qt import translate

    return translate("Audio Volume", "Volume {PERCENT}%").format(
        PERCENT=volume_percent(volume)
    )
