"""Always the bundled yt_dlp module unless the owner opts into a binary."""

from pathlib import Path

from gridplayer.settings import Settings


def bundled_module_name() -> str:
    return "yt_dlp"


def external_binary() -> Path | None:
    """An owner-chosen yt-dlp executable, or None to use the bundled module.

    PATH is never searched. An empty setting is the bundled module.
    """

    try:
        raw = Settings().get("streaming/ytdlp_external_path")
    except (KeyError, ValueError):
        return None

    path = Path(str(raw or "")).expanduser()
    if not str(path) or not path.is_file():
        return None

    return path
