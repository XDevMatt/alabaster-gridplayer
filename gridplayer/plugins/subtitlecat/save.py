"""Where a downloaded subtitle file is written.

Beside the video when that folder can be written. Otherwise the Alabaster
data folder's subtitles directory. The bytes are written as received.
"""

import secrets
from pathlib import Path

from gridplayer.utils.app_dir import get_app_data_dir
from gridplayer.utils.qt import translate


class SaveError(Exception):
    """The subtitle could not be written."""


def subtitle_folder(video_uri, data_dir: Path | None = None) -> Path:
    """The folder a subtitle for this video is saved in."""

    if isinstance(video_uri, Path) and video_uri.is_absolute():
        folder = video_uri.parent
        if folder_is_writable(folder):
            return folder

    root = data_dir if data_dir is not None else get_app_data_dir()
    fallback = root / "subtitles"

    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise SaveError(
            translate("SubtitleCat", "Nowhere to save the subtitle.")
        ) from None

    if folder_is_writable(fallback):
        return fallback

    raise SaveError(translate("SubtitleCat", "Nowhere to save the subtitle."))


def unique_path(folder: Path, name: str) -> Path:
    """``name`` in ``folder``, or ``name-2`` when that file is already there."""

    if "/" in name or "\\" in name or name in {".", ".."}:
        raise SaveError(translate("SubtitleCat", "That subtitle name is not usable."))

    candidate = folder / name

    if not candidate.exists():
        return candidate

    stem = name[:-4] if name.casefold().endswith(".srt") else name
    number = 2

    while number <= 1000:
        candidate = folder / f"{stem}-{number}.srt"
        if not candidate.exists():
            return candidate
        number += 1

    raise SaveError(translate("SubtitleCat", "Nowhere to save the subtitle."))


def save_bytes(folder: Path, name: str, body: bytes) -> Path:
    path = unique_path(folder, name)
    path.write_bytes(body)
    return path


def folder_is_writable(folder: Path) -> bool:
    """Try a probe file. ``os.access`` is the wrong test on Windows."""

    if not folder.is_dir():
        return False

    probe = folder / f".gp-subtitle-probe-{secrets.token_hex(4)}"

    try:
        probe.write_bytes(b"")
    except OSError:
        return False

    try:
        probe.unlink()
    except OSError:
        return True

    return True
