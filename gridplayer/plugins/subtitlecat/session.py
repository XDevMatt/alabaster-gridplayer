"""subtitlecat.com cookies for one request.

Read from the browser named on the Cookies page, through yt-dlp's reader,
and only when a request is about to be made. The copy stays in memory.
Nothing here writes a cookie jar, a setting, or a log line.
"""

import http.cookiejar

from gridplayer.settings import Settings
from gridplayer.utils.qt import translate

BROWSER_LABELS = {
    "brave": "Brave",
    "chrome": "Chrome",
    "chromium": "Chromium",
    "edge": "Edge",
    "firefox": "Firefox",
    "opera": "Opera",
    "safari": "Safari",
    "vivaldi": "Vivaldi",
    "whale": "Whale",
}

# A cookie whose name looks like a login. Analytics and Cloudflare cookies
# are not a login, even when they are sent along with one.
_LOGIN_NAMES = frozenset(
    {
        "phpsessid",
        "sess",
        "session",
        "sessionid",
        "session_id",
        "remember",
        "remember_me",
        "rememberme",
        "auth",
        "auth_token",
        "token",
        "user",
        "userid",
        "user_id",
        "logged_in",
        "login",
        "subtitlecat",
    }
)
_LOGIN_PARTS = ("sess", "auth", "login", "remember", "token", "user")
_ANALYTICS_EXACT = frozenset(
    {
        "_ga",
        "_gid",
        "_gat",
        "_gcl_au",
        "_fbp",
        "__cf_bm",
        "cf_clearance",
        "__cflb",
        "__cfduid",
    }
)


class _QuietLogger:
    """A yt-dlp logger that keeps cookie paths and values off the log."""

    def debug(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def stdout(self, *args, **kwargs):
        return None

    def stderr(self, *args, **kwargs):
        return None


def browser_label(name: str) -> str:
    key = (name or "").strip().casefold()

    if not key:
        return ""

    return BROWSER_LABELS.get(key, key.title())


def sign_in_message(browser: str) -> str:
    """The sentence shown when there is nothing to send a request with."""

    label = browser_label(browser)

    if not label:
        return translate(
            "SubtitleCat",
            "Choose a browser on the Cookies page, then sign in to SubtitleCat there first",
        )

    template = translate("SubtitleCat", "Sign in to SubtitleCat in {browser} first")
    return template.replace("{browser}", label)


def configured_browser() -> tuple[str, str | None]:
    browser = _text_setting("cookies/from_browser").casefold()
    profile = _text_setting("cookies/browser_profile") or None
    return browser, profile


def read_for_request(reader=None) -> tuple[http.cookiejar.CookieJar, bool, str]:
    """subtitlecat.com cookies, whether any of them is a login, and the browser.

    No browser configured means no read and no login. The source jar is
    cleared after the copy. The copy is not saved.
    """

    browser, profile = configured_browser()

    if not browser:
        return http.cookiejar.CookieJar(), False, ""

    source = (reader or _ytdlp_reader)(browser, profile)

    try:
        kept, logged_in = take_subtitlecat_cookies(source)
    finally:
        _clear_jar(source)

    return kept, logged_in, browser


def take_subtitlecat_cookies(source) -> tuple[http.cookiejar.CookieJar, bool]:
    """Copy subtitlecat.com cookies into a plain jar. Never calls ``save``."""

    kept = http.cookiejar.CookieJar()
    logged_in = False

    for cookie in list(source):
        if not _subtitlecat_domain(getattr(cookie, "domain", "")):
            continue

        kept.set_cookie(cookie)

        if _is_login_cookie(cookie.name):
            logged_in = True

    return kept, logged_in


def _ytdlp_reader(browser: str, profile: str | None):
    # Imported here: yt-dlp stays out of the process until a request.
    from yt_dlp.cookies import extract_cookies_from_browser

    from gridplayer.utils.percent_re import untangle_percent_re

    # yt-dlp patches urllib3 as it is imported; see utils/percent_re.py.
    # Left broken, the SubtitleCat requests made right after this (and every
    # other request in the app) would fail on the first host name.
    untangle_percent_re()

    return extract_cookies_from_browser(browser, profile, _QuietLogger())


def _text_setting(name: str) -> str:
    try:
        value = Settings().get(name)
    except (KeyError, ValueError, TypeError):
        return ""

    if not isinstance(value, str):
        return ""

    return value.strip()


def _subtitlecat_domain(domain: str) -> bool:
    host = (domain or "").lstrip(".").casefold()
    return host == "subtitlecat.com" or host.endswith(".subtitlecat.com")


def _is_analytics(name: str) -> bool:
    folded = name.casefold()

    if folded in _ANALYTICS_EXACT:
        return True

    return folded.startswith(("_ga", "_gid", "_gat", "__cf", "cf_"))


def _is_login_cookie(name: str) -> bool:
    folded = (name or "").casefold()

    if not folded or _is_analytics(folded):
        return False

    if folded in _LOGIN_NAMES:
        return True

    return any(part in folded for part in _LOGIN_PARTS)


def _clear_jar(jar) -> None:
    clear = getattr(jar, "clear", None)

    if callable(clear):
        clear()
