"""Read SubtitleCat's public search and subtitle pages.

The pages are parsed here. Nothing in this module fetches one.
"""

import json
import re
import urllib.parse
from dataclasses import dataclass
from html.parser import HTMLParser

ALLOWED_HOSTS = frozenset({"subtitlecat.com", "www.subtitlecat.com"})
ORIGIN = "https://www.subtitlecat.com"

_PAGE = re.compile(r"/subs/\d+/[^/]+\.html$", re.IGNORECASE)
_SIZE = re.compile(r"Size\s+(\d+(?:\.\d+)?\s*[KMG]?B)", re.IGNORECASE)
_DOWNLOADS = re.compile(r"Downloads\s+(\d+)", re.IGNORECASE)
_LANGUAGES = re.compile(r"Languages\s+(\d+)", re.IGNORECASE)
_SOURCE = re.compile(r"translated from\s+([^)]+)", re.IGNORECASE)
_TRANSLATE = re.compile(
    r"""translate_from_server_folder\(\s*['"]([^'"]*)['"]\s*,"""
    r"""\s*['"]([^'"]*)['"]\s*,\s*['"]([^'"]*)['"]\s*\)"""
)
_MESSAGE_CAP = 8000


@dataclass(frozen=True)
class SearchHit:
    title: str
    href: str
    size: str
    downloads: str
    languages: str
    source_language: str


@dataclass(frozen=True)
class TranslateRequest:
    """What a Translate button on the page named. Not a request by itself."""

    language: str
    filename: str
    folder: str


@dataclass(frozen=True)
class LanguageRow:
    code: str
    name: str
    download_url: str | None
    translate: TranslateRequest | None


def absolute_subtitlecat(href: str) -> str | None:
    """An https URL on subtitlecat.com, or None when the link points away."""

    text = (href or "").strip()

    if not text or text.startswith(("//", "javascript:", "data:")):
        return None

    if text.startswith(("http://", "https://")):
        parts = urllib.parse.urlsplit(text)
        host = (parts.hostname or "").casefold()
        if parts.scheme != "https" or host not in ALLOWED_HOSTS:
            return None
        return urllib.parse.urlunsplit(parts)

    if text.startswith("/"):
        return ORIGIN + text

    if text.startswith("subs/"):
        return ORIGIN + "/" + text

    return None


def parse_search(html: str) -> tuple[SearchHit, ...]:
    parser = _SearchParser()
    parser.feed(html)
    parser.close()
    return tuple(parser.hits)


def parse_detail(html: str) -> tuple[LanguageRow, ...]:
    parser = _DetailParser()
    parser.feed(html)
    parser.close()
    return tuple(parser.rows)


def message_from_response(content_type: str, body: bytes) -> str:
    """SubtitleCat's answer as text, without rewriting a JSON body."""

    text = body.decode("utf-8", errors="replace").strip()

    if not text:
        return ""

    kind = (content_type or "").casefold()
    head = text.lstrip()

    if "json" in kind or head[:1] in {"{", "["}:
        return text[:_MESSAGE_CAP]

    if "html" in kind or head[:1] == "<":
        return visible_text(text)[:_MESSAGE_CAP]

    return text[:_MESSAGE_CAP]


def visible_text(html: str) -> str:
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return " ".join("".join(parser.parts).split())


def srt_url_from_json(text: str) -> str | None:
    """A subtitlecat.com ``.srt`` named in a JSON object, if there is one."""

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    found: list[str] = []

    def walk(node) -> None:
        if isinstance(node, str):
            found.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)

    for item in found:
        url = absolute_subtitlecat(item)
        if url and url.split("?", 1)[0].casefold().endswith(".srt"):
            return url

    return None


def is_subtitle_payload(content_type: str, body: bytes) -> bool:
    """Whether these bytes are a subtitle file rather than an HTML page."""

    if "html" in (content_type or "").casefold():
        return False

    sample = body.lstrip()[:4000]
    head = sample[:20].lower()

    if head.startswith((b"<!doctype", b"<html", b"<head")):
        return False

    if b"-->" in sample:
        return True

    if sample.startswith((b"WEBVTT", b"\xef\xbb\xbfWEBVTT")):
        return True

    text = sample.decode("utf-8", errors="replace")

    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.isdigit()

    return False


def preferred_language_codes(
    subtitle_languages: str, player_language: str
) -> tuple[str, ...]:
    """The user's subtitle languages, or the player's language when unset."""

    codes = [
        part.replace("_", "-")
        for part in re.split(r"[,;\s]+", (subtitle_languages or "").strip())
        if part
    ]

    if codes:
        return tuple(codes)

    primary = (player_language or "").replace("_", "-").split("-")[0]
    if primary:
        return (primary,)

    return ()


def order_languages(
    rows: tuple[LanguageRow, ...] | list[LanguageRow],
    preferred: tuple[str, ...] | list[str],
) -> tuple[LanguageRow, ...]:
    """Preferred languages first. A regional code matches only itself.

    ``en`` matches ``en`` and ``en-GB``. ``zh`` matches ``zh-CN`` and
    ``zh-TW``. ``zh-TW`` does not match ``zh-CN``.
    """

    ranked = sorted(
        rows,
        key=lambda row: (
            *_language_rank(row.code, preferred),
            row.name.casefold(),
        ),
    )
    return tuple(ranked)


def _language_rank(code: str, preferred) -> tuple[int, int]:
    norm = _norm(code)
    primary = norm.split("-")[0]

    for index, want in enumerate(preferred):
        want_norm = _norm(want)
        if norm == want_norm:
            return (0, index)
        if "-" not in want_norm and want_norm == primary:
            return (1, index)

    return (2, 0)


def _norm(code: str) -> str:
    return code.strip().replace("_", "-").casefold()


def _is_subtitle_page(url: str) -> bool:
    return _PAGE.search(urllib.parse.urlsplit(url).path) is not None


def _first(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if match is None:
        return ""
    return " ".join(match.group(1).split())


class _SearchParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hits: list[SearchHit] = []
        self._in_row = False
        self._row_parts: list[str] = []
        self._row_href: str | None = None
        self._row_title: str | None = None
        self._in_link = False
        self._link_is_hit = False
        self._link_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "tr":
            self._in_row = True
            self._row_parts = []
            self._row_href = None
            self._row_title = None

        if tag == "a" and self._in_row:
            self._in_link = True
            self._link_parts = []
            absolute = absolute_subtitlecat(attributes.get("href", ""))
            self._link_is_hit = bool(absolute and _is_subtitle_page(absolute))
            if self._link_is_hit:
                self._row_href = absolute

    def handle_endtag(self, tag):
        if tag == "a" and self._in_link:
            if self._link_is_hit and self._row_title is None:
                self._row_title = "".join(self._link_parts).strip()
            self._in_link = False
            self._link_is_hit = False

        if tag == "tr" and self._in_row:
            if self._row_href:
                text = "".join(self._row_parts)
                self.hits.append(
                    SearchHit(
                        title=_clean_title(self._row_title or ""),
                        href=self._row_href,
                        size=_first(_SIZE, text),
                        downloads=_first(_DOWNLOADS, text),
                        languages=_first(_LANGUAGES, text),
                        source_language=_first(_SOURCE, text),
                    )
                )
            self._in_row = False

    def handle_data(self, data):
        if self._in_row:
            self._row_parts.append(data)
        if self._in_link:
            self._link_parts.append(data)


class _DetailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[LanguageRow] = []
        self._depth = 0
        self._parts: list[str] = []
        self._code = ""
        self._download: str | None = None
        self._translate: TranslateRequest | None = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "div" and "sub-single" in classes and self._depth == 0:
            self._depth = 1
            self._parts = []
            self._code = ""
            self._download = None
            self._translate = None
            return

        if not self._depth:
            return

        if tag == "div":
            self._depth += 1

        if tag == "img" and "flag" in classes:
            self._code = attributes.get("alt", "") or self._code

        element_id = attributes.get("id", "")

        if tag == "a" and element_id.startswith("download_"):
            href = absolute_subtitlecat(attributes.get("href", ""))
            if href and href.split("?", 1)[0].casefold().endswith(".srt"):
                self._download = href
                self._code = element_id[len("download_") :] or self._code

        if tag == "button":
            match = _TRANSLATE.search(attributes.get("onclick", ""))
            if match:
                language, filename, folder = match.groups()
                self._translate = TranslateRequest(language, filename, folder)
                self._code = self._code or element_id or language

    def handle_endtag(self, tag):
        if self._depth and tag == "div":
            self._depth -= 1
            if self._depth == 0 and (self._code or self._download or self._translate):
                self.rows.append(
                    LanguageRow(
                        code=self._code,
                        name=_language_name(self._parts),
                        download_url=self._download,
                        translate=self._translate,
                    )
                )

    def handle_data(self, data):
        if self._depth:
            self._parts.append(data)


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def _clean_title(title: str) -> str:
    cleaned = re.sub(
        r"\s*\(translated from [^)]*\)\s*",
        " ",
        title,
        flags=re.IGNORECASE,
    )
    return " ".join(cleaned.split())


def _language_name(parts: list[str]) -> str:
    text = " ".join("".join(parts).split())
    text = re.sub(r"\b(Download|Translate)\b", "", text)
    return " ".join(text.split())
