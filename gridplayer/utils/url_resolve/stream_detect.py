import contextlib
import itertools
import re
import urllib.error
import urllib.request

from gridplayer.utils.network import DEFAULT_USER_AGENT
from gridplayer.utils.stream_proxy.mp4 import is_fragmented
from gridplayer.utils.url_resolve.static import BadURLException

MANIFEST_HEAD = 4096
FILE_HEAD = 64 * 1024
PLAYLIST_READ_LIMIT = 2 * 1024 * 1024
PROBE_TIMEOUT_S = 30


def _headers(session_headers: dict[str, str] | None) -> dict[str, str]:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if session_headers:
        headers.update(session_headers)
    return headers


def _open_url(url: str, session=None, session_headers=None, extra_headers=None):
    """A readable response, without importing Streamlink on the default path.

    A caller that already holds a Streamlink session (the future plugin)
    can pass it; everything else uses urllib.
    """

    headers = _headers(session_headers)
    if extra_headers:
        headers.update(extra_headers)

    if session is not None and hasattr(session, "http"):
        return session.http.get(
            url, headers=headers, stream=True, timeout=PROBE_TIMEOUT_S
        )

    request = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(request, timeout=PROBE_TIMEOUT_S)


def _read_limited(response, limit: int) -> bytes:
    if hasattr(response, "raw"):
        return response.raw.read(limit) or b""
    return response.read(limit) or b""


def is_hls_live_stream(
    url: str,
    session=None,
    session_headers: dict[str, str] | None = None,
) -> bool:
    try:
        response = _open_url(url, session, session_headers)
    except (OSError, urllib.error.URLError) as e:
        raise BadURLException(f"Cannot open URL {url}") from e

    with contextlib.closing(response):
        body = _read_limited(response, PLAYLIST_READ_LIMIT).decode(
            "utf-8", errors="replace"
        )

    lines = body.splitlines()
    playlist_header = "\n".join(lines[:20])

    if "#EXT-X-TWITCH-LIVE-SEQUENCE" in playlist_header:
        return True

    if "#EXT-X-PLAYLIST-TYPE:VOD" in playlist_header:
        return False

    if re.search("#EXT-X-MEDIA-SEQUENCE:0$", playlist_header, re.M):
        return False

    if not re.search(r"#EXT-X-MEDIA-SEQUENCE:[\d.]+$", playlist_header, re.M):
        return False

    return not _has_endlist(itertools.chain(playlist_header.splitlines(), lines))


def _has_endlist(lines) -> bool:
    return any(line.strip() == "#EXT-X-ENDLIST" for line in lines)


def is_dash_live_stream(
    url: str,
    session=None,
    session_headers: dict[str, str] | None = None,
) -> bool:
    """A DASH manifest is live when it declares itself dynamic."""

    try:
        response = _open_url(url, session, session_headers)
    except (OSError, urllib.error.URLError) as e:
        raise BadURLException(f"Cannot open URL {url}") from e

    with contextlib.closing(response):
        manifest = _read_limited(response, MANIFEST_HEAD).decode(
            "utf-8", errors="replace"
        )

    return bool(re.search(r'type\s*=\s*"dynamic"', manifest[:MANIFEST_HEAD]))


def is_fragmented_stream(
    url: str,
    session=None,
    session_headers: dict[str, str] | None = None,
) -> bool:
    """Whether a plain file is fragmented, and so can be cut into segments."""

    try:
        response = _open_url(
            url,
            session,
            session_headers,
            extra_headers={"Range": f"bytes=0-{FILE_HEAD - 1}"},
        )
    except (OSError, urllib.error.URLError) as e:
        raise BadURLException(f"Cannot open URL {url}") from e

    with contextlib.closing(response):
        return is_fragmented(_read_limited(response, FILE_HEAD))


def is_http_live_stream(
    url: str,
    session=None,
    session_headers: dict[str, str] | None = None,
) -> bool:
    """if there is a content-length header, it not a stream"""

    try:
        response = _open_url(url, session, session_headers)
    except (OSError, urllib.error.URLError) as e:
        raise BadURLException(f"Cannot open URL {url}") from e

    with contextlib.closing(response):
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            raise BadURLException(f"URL returned html page {url}")
        size = int(response.headers.get("Content-Length", 0) or 0)

    return size == 0
