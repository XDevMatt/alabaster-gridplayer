"""Where a downloaded subtitle file is written.

Beside the video when that folder can be written. Otherwise the Alabaster
data folder's subtitles directory. The bytes are written as received, except
that a UTF-8 file with a few broken bytes in it is repaired first; see
``repair_stray_bytes``.
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
    path.write_bytes(repair_stray_bytes(body))
    return path


def repair_stray_bytes(body: bytes) -> bytes:
    """A mostly UTF-8 subtitle with its few invalid bytes made valid.

    libVLC (3.0) reads a text subtitle as UTF-8 only until the first cue that
    is not valid UTF-8. From that cue on it converts every cue from the
    fallback character set (the encoding setting, Windows-1252 when that is
    empty), and a cue that does not convert -- UTF-8 Greek, Cyrillic, CJK, or
    a closing curly quote all carry bytes Windows-1252 lacks -- is dropped
    without a word. One stray byte in a SubtitleCat file blanks the rest of
    it. Naming UTF-8 by hand avoided that, which is why it looked like the
    fix.

    So a file that is UTF-8 apart from a few bytes is written as clean UTF-8,
    each stray byte read as the Windows-1252 character it most likely was.
    Valid UTF-8, UTF-16, and files in some other character set are left
    exactly as they are, so the encoding setting still decides those.
    """

    if body.startswith((b"\xff\xfe", b"\xfe\xff")):
        return body

    try:
        body.decode("utf-8")
    except UnicodeDecodeError:
        pass
    else:
        return body

    text = body.decode("utf-8", errors="surrogateescape")
    stray = sum(1 for ch in text if _is_stray(ch))
    multibyte = sum(1 for ch in text if ch > "\x7f" and not _is_stray(ch))

    # A legacy file has next to no valid multibyte sequences in it.
    if multibyte <= stray:
        return body

    return "".join(_from_cp1252(ch) if _is_stray(ch) else ch for ch in text).encode(
        "utf-8"
    )


def _is_stray(ch: str) -> bool:
    return "\udc80" <= ch <= "\udcff"


def _from_cp1252(ch: str) -> str:
    return bytes([ord(ch) - 0xDC00]).decode("cp1252", errors="replace")


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
