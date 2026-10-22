"""Search words and subtitle file names.

Apostrophes are dropped so the letters join: Britain's becomes Britains.
A name taken from a page is only the last path segment, then cleaned.
"""

import urllib.parse

# Characters that stand in for an apostrophe. Dropped, not turned into a
# space, so the letters on either side join.
# ASCII apostrophe, then the typographic marks people type instead of one.
_APOSTROPHES = "'\u2019\u2018\u02bc\u00b4`\u02b9\u2032"

_INVALID = '<>:"|?*'

# Windows device names. A file with one of these is not a file.
_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def drop_apostrophes(text: str) -> str:
    for mark in _APOSTROPHES:
        text = text.replace(mark, "")
    return text


def search_terms(file_name: str) -> str:
    """Words to put in the search box, taken from a file name or a title."""

    base = file_name.replace("\\", "/").rsplit("/", 1)[-1]
    stem = _stem(base)
    stem = drop_apostrophes(stem)
    stem = stem.replace(".", " ").replace("_", " ")
    return " ".join(stem.split())


def name_from_url(url: str) -> str:
    """The file name at the end of a subtitle URL."""

    path = urllib.parse.urlsplit(url).path
    return safe_subtitle_name(path)


def safe_subtitle_name(raw: str) -> str:
    """A single ``.srt`` name that cannot leave the folder it is saved in."""

    text = str(raw).replace("\\", "/")
    text = text.rsplit("/", 1)[-1]
    text = urllib.parse.unquote(text)
    text = drop_apostrophes(text)

    cleaned = []
    for char in text:
        if char in _INVALID or char in {"/", "\\"} or ord(char) < 32:
            continue
        cleaned.append(char)

    name = "".join(cleaned).strip().strip(".")

    if not name or name in {".", ".."}:
        name = "subtitle"

    stem = name[:-4] if name.casefold().endswith(".srt") else name
    if stem.casefold() in _RESERVED or not stem:
        name = "subtitle.srt"
    elif not name.casefold().endswith(".srt"):
        name = name + ".srt"

    return name


def _stem(base: str) -> str:
    if "." not in base:
        return base

    stem, ext = base.rsplit(".", 1)

    if stem and ext.isascii() and ext.isalnum() and len(ext) <= 5:
        return stem

    return base
