"""Request-time browser cookies for yt-dlp. There is no stored jar.

yt-dlp may read the current cookies from the owner's chosen browser when
a link is resolved (`--cookies-from-browser`). Those stay in memory for
that resolve. A leftover cookies.txt in the data dir is not read or
written.
"""

import contextlib
import logging

from gridplayer.settings import Settings
from gridplayer.utils.app_dir import get_app_data_dir

COOKIE_FILE_NAME = "cookies.txt"

_log = logging.getLogger(__name__)


def leftover_cookie_file():
    """Where an old stored jar would sit. Not read, not deleted."""

    return get_app_data_dir() / COOKIE_FILE_NAME


def has_cookies_for(url: str) -> bool:
    """No stored jar, so nothing is sent from disk."""

    return False


def cookies_stamp() -> tuple | None:
    return None


def apply_to_streamlink(session) -> None:
    """Stored cookies are gone. The Streamlink plugin gets none from core."""

    return


def browser_cookie_opts(browser: str | None, profile: str | None = None) -> dict:
    """yt-dlp's ``cookiesfrombrowser`` option, or nothing when no browser is set.

    The tuple is what ``--cookies-from-browser`` becomes. yt-dlp reads the
    browser when a link is resolved. Nothing is written here.
    """

    name = (browser or "").strip().lower()

    if not name:
        return {}

    chosen = (profile or "").strip() or None

    return {"cookiesfrombrowser": (name, chosen, None, None)}


def _configured_browser_cookie_opts() -> dict:
    return browser_cookie_opts(
        _text_setting("cookies/from_browser"),
        _text_setting("cookies/browser_profile"),
    )


def _text_setting(name: str) -> str:
    try:
        value = Settings().get(name)
    except (KeyError, ValueError):
        return ""

    return value if isinstance(value, str) else ""


@contextlib.contextmanager
def ytdl_cookies():
    """Cookie options for a YoutubeDL: browser cookies, in memory only."""

    yield _configured_browser_cookie_opts()
