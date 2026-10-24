"""A cell's volume: kept in whole percents, never past 100% (VLC itself goes
to 125%), and stepped by the player/volume_step setting. Mute is 0%.

No Qt imported at the top: the VLC player processes use this too.
"""

STEP_SETTING = "player/volume_step"

MIN_STEP = 1
MAX_STEP = 25
# 3%: at 5% one step was too quiet and the next too loud
DEFAULT_STEP = 3
# the default until 2026-10-23; a stored one is moved to the new default once
OLD_DEFAULT_STEP = 5


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


def mute_as_zero(is_muted, volume) -> tuple[bool, float]:
    """Mute is volume 0, and volume 0 is mute: the one pair a cell may be in.

    There is no level kept behind mute: a muted cell is at 0%, however it
    was saved or set.
    """

    volume = clamp_volume(volume)

    if is_muted or volume == 0:
        return True, 0.0

    return False, volume


def volume_txt(volume) -> str:
    """What the cell says as its volume changes: "Volume 17%"."""

    from gridplayer.utils.qt import translate

    return translate("Audio Volume", "Volume {PERCENT}%").format(
        PERCENT=volume_percent(volume)
    )
