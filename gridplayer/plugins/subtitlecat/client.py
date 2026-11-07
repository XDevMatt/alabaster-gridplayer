"""One SubtitleCat request at a time, and only after a user action.

The plugin setting is checked before cookies are read and before any
request. A missing session means no request. A limit or a VIP reply is
returned as SubtitleCat sent it. Nothing here retries, and nothing here
calls out to a translator of its own.

Translate is one POST of the language and the file the page's button
named. The subtitle text is not sent.
"""

import http.client
import logging
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from gridplayer.params.static import ProxyMode
from gridplayer.plugins.subtitlecat.names import name_from_url
from gridplayer.plugins.subtitlecat.parse import (
    LanguageRow,
    SearchHit,
    TranslateRequest,
    is_subtitle_payload,
    message_from_response,
    parse_detail,
    parse_search,
    srt_url_from_json,
)
from gridplayer.plugins.subtitlecat.session import read_for_request, sign_in_message
from gridplayer.utils.network import (
    IPV4_SOURCE_ADDRESS,
    NetworkOpts,
    network_opts,
    vlc_user_agent,
)
from gridplayer.utils.qt import translate

_log = logging.getLogger(__name__)

ORIGIN = "https://www.subtitlecat.com/"
SEARCH_URL = "https://www.subtitlecat.com/index.php"
TRANSLATE_URL = "https://www.subtitlecat.com/request_shared_translation.php"
ALLOWED_HOSTS = frozenset({"subtitlecat.com", "www.subtitlecat.com"})

HTML_LIMIT = 2 * 1024 * 1024
DOWNLOAD_LIMIT = 8 * 1024 * 1024
DEFAULT_TIMEOUT_SEC = 20
MIN_GAP_SEC = 1.0


class SubtitleCatError(Exception):
    """A SubtitleCat problem the dialog can show as text."""


class PluginOff(SubtitleCatError):
    def __init__(self):
        super().__init__(
            translate("SubtitleCat", "SubtitleCat.com is turned off in Settings.")
        )


class TranslateOff(SubtitleCatError):
    def __init__(self):
        super().__init__(
            translate(
                "SubtitleCat",
                "Requesting a translation is turned off in Settings.",
            )
        )


class NoSession(SubtitleCatError):
    def __init__(self, browser: str):
        self.browser = browser
        super().__init__(sign_in_message(browser))


class TimedOut(SubtitleCatError):
    def __init__(self):
        super().__init__(
            translate("SubtitleCat", "SubtitleCat.com did not answer in time.")
        )


class EmptySearch(SubtitleCatError):
    def __init__(self):
        super().__init__(translate("SubtitleCat", "Enter a title to search for."))


@dataclass(frozen=True)
class SearchOutcome:
    hits: tuple[SearchHit, ...]
    message: str


@dataclass(frozen=True)
class PageOutcome:
    languages: tuple[LanguageRow, ...]
    message: str


@dataclass(frozen=True)
class DownloadOutcome:
    """``kind`` is ``subtitle`` or ``message``. A message is not saved."""

    kind: str
    body: bytes
    message: str
    filename: str


@dataclass(frozen=True)
class TranslateOutcome:
    """The site's reply. ``download_url`` is fetched only if the user asks."""

    text: str
    download_url: str | None = None
    body: bytes | None = None
    filename: str = ""


class PoliteGate:
    """One call at a time, and at least ``min_gap`` seconds between them."""

    def __init__(self, min_gap=MIN_GAP_SEC, clock=time.monotonic, sleep=time.sleep):
        self._min_gap = min_gap
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._next_ok = None

    def run(self, function):
        with self._lock:
            now = self._clock()

            if self._next_ok is not None:
                delay = self._next_ok - now
                if delay > 0:
                    self._sleep(delay)

            try:
                return function()
            finally:
                self._next_ok = self._clock() + self._min_gap


class SubtitleCatClient:
    """Search, page, download, and translate. Each is one request."""

    def __init__(
        self,
        *,
        settings_get=None,
        session=None,
        transport=None,
        gate=None,
        opts=None,
        user_agent=None,
    ):
        self._settings_get = settings_get
        self._session = session or read_for_request
        self._transport = transport
        self._gate = gate or PoliteGate()
        self._opts = opts
        self._user_agent = user_agent

    def search(self, terms: str, referer: str = ORIGIN) -> SearchOutcome:
        self._require_plugin()
        words = (terms or "").strip()

        if not words:
            raise EmptySearch

        query = urllib.parse.urlencode({"search": words})
        url = SEARCH_URL + "?" + query
        status, content_type, body = self._fetch("GET", url, referer, None, HTML_LIMIT)
        html = body.decode("utf-8", errors="replace")
        hits = parse_search(html)

        if hits:
            return SearchOutcome(hits, "")

        return SearchOutcome((), _message(status, content_type, body))

    def page(self, url: str, referer: str = ORIGIN) -> PageOutcome:
        self._require_plugin()
        status, content_type, body = self._fetch("GET", url, referer, None, HTML_LIMIT)
        html = body.decode("utf-8", errors="replace")
        languages = parse_detail(html)

        if languages:
            return PageOutcome(languages, "")

        return PageOutcome((), _message(status, content_type, body))

    def download(self, url: str, referer: str) -> DownloadOutcome:
        self._require_plugin()
        status, content_type, body = self._fetch(
            "GET", url, referer, None, DOWNLOAD_LIMIT
        )
        filename = name_from_url(url)

        if is_subtitle_payload(content_type, body):
            return DownloadOutcome("subtitle", body, "", filename)

        return DownloadOutcome(
            "message", b"", _message(status, content_type, body), filename
        )

    def translate(self, request: TranslateRequest, page_url: str) -> TranslateOutcome:
        self._require_plugin()

        if not self._setting("plugins/subtitlecat_translate"):
            raise TranslateOff

        if not request.language or not request.filename or not request.folder:
            raise SubtitleCatError(
                translate("SubtitleCat", "That language cannot be requested.")
            )

        # The button's language and file identity only. Not the subtitle
        # text, and not a second try when the answer is a limit.
        payload = urllib.parse.urlencode(
            {
                "to_language": request.language,
                "filename": request.filename,
                "folder": request.folder,
            }
        ).encode("ascii")
        status, content_type, body = self._fetch(
            "POST", TRANSLATE_URL, page_url, payload, HTML_LIMIT
        )
        text = _message(status, content_type, body)

        if is_subtitle_payload(content_type, body):
            return TranslateOutcome(
                text=translate(
                    "SubtitleCat",
                    "A subtitle is ready. Choose Download to save it.",
                ),
                body=body,
                filename=name_from_url(request.filename),
            )

        download_url = None
        if text.lstrip()[:1] in {"{", "["}:
            download_url = srt_url_from_json(text)

        return TranslateOutcome(text=text, download_url=download_url)

    def _require_plugin(self) -> None:
        if not self._setting("plugins/subtitlecat"):
            raise PluginOff

    def _setting(self, key: str) -> bool:
        getter = self._settings_get or _settings_get

        try:
            return bool(getter(key))
        except (KeyError, ValueError, TypeError):
            return False

    def _fetch(self, method, url, referer, data, limit):
        if not allowed_url(url):
            raise SubtitleCatError(
                translate("SubtitleCat", "That address is not on SubtitleCat.com.")
            )

        jar, logged_in, browser = self._session()

        try:
            if not logged_in:
                raise NoSession(browser)

            return self._gate.run(
                lambda: self._once(method, url, referer, data, limit, jar)
            )
        finally:
            jar.clear()

    def _once(self, method, url, referer, data, limit, jar):
        headers = {"User-Agent": self._agent()}
        referer_url = _same_site(referer)

        if referer_url:
            headers["Referer"] = referer_url

        cookie_header = _cookie_header(jar, url)

        if cookie_header:
            headers["Cookie"] = cookie_header

        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        transport = self._transport or self._urllib
        return transport(method, url, headers, data, self._timeout(), limit)

    def _urllib(self, method, url, headers, data, timeout, limit):
        request = urllib.request.Request(url, data=data, method=method)

        for key, value in headers.items():
            request.add_header(key, value)

        opener = _opener(self._network_opts())

        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc
        except TimeoutError:
            _log.debug("SubtitleCat request failed: %s", "timeout")
            raise TimedOut from None
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, TimeoutError):
                _log.debug("SubtitleCat request failed: %s", type(reason).__name__)
                raise TimedOut from None
            _log.debug(
                "SubtitleCat request failed: %s",
                type(reason).__name__ if reason is not None else "URLError",
            )
            raise SubtitleCatError(
                translate("SubtitleCat", "SubtitleCat.com could not be reached.")
            ) from None
        except OSError as exc:
            _log.debug("SubtitleCat request failed: %s", type(exc).__name__)
            raise SubtitleCatError(
                translate("SubtitleCat", "SubtitleCat.com could not be reached.")
            ) from None

        try:
            status = getattr(response, "status", None) or response.code
            content_type = response.headers.get("Content-Type", "")
            body = _read_capped(response, limit)
        finally:
            response.close()

        return status, content_type, body

    def _agent(self) -> str:
        if self._user_agent:
            return self._user_agent

        return vlc_user_agent()

    def _timeout(self) -> int:
        opts = self._network_opts()

        if opts.timeout and opts.timeout > 0:
            return int(opts.timeout)

        return DEFAULT_TIMEOUT_SEC

    def _network_opts(self) -> NetworkOpts:
        if self._opts is not None:
            return self._opts

        return network_opts()


def allowed_url(url: str) -> bool:
    parts = urllib.parse.urlsplit(url or "")
    host = (parts.hostname or "").casefold()
    return parts.scheme == "https" and host in ALLOWED_HOSTS


class HostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only when it stays on subtitlecat.com.

    An off-site redirect is refused before a new request exists, so the
    cookie header is not copied onto it.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(req.full_url, newurl)

        if not allowed_url(target):
            raise SubtitleCatError(
                translate("SubtitleCat", "That address is not on SubtitleCat.com.")
            )

        return super().redirect_request(req, fp, code, msg, headers, target)


def _opener(opts: NetworkOpts):
    handlers = []

    if opts.proxy_mode is ProxyMode.NONE:
        # Any ProxyHandler stops urllib from adding the machine's. An
        # empty map then adds no proxy address of its own.
        handlers.append(urllib.request.ProxyHandler({}))
    elif opts.proxy_mode is ProxyMode.CUSTOM and opts.proxy:
        handlers.append(
            urllib.request.ProxyHandler({"http": opts.proxy, "https": opts.proxy})
        )
    else:
        handlers.append(urllib.request.ProxyHandler())

    context = None if opts.verify_tls else ssl._create_unverified_context()

    if opts.force_ipv4:
        handlers.append(_IPv4HTTPHandler())
        handlers.append(_IPv4HTTPSHandler(context=context))
    elif context is not None:
        handlers.append(urllib.request.HTTPSHandler(context=context))

    handlers.append(HostRedirectHandler())
    return urllib.request.build_opener(*handlers)


class _IPv4HTTPConnection(http.client.HTTPConnection):
    def __init__(self, *args, **kwargs):
        kwargs["source_address"] = (IPV4_SOURCE_ADDRESS, 0)
        super().__init__(*args, **kwargs)


class _IPv4HTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        kwargs["source_address"] = (IPV4_SOURCE_ADDRESS, 0)
        super().__init__(*args, **kwargs)


class _IPv4HTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_IPv4HTTPConnection, req)


class _IPv4HTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_IPv4HTTPSConnection, req, context=self._context)


def _settings_get(key: str):
    from gridplayer.settings import Settings

    return Settings().get(key)


def _same_site(url: str) -> str | None:
    if url and allowed_url(url):
        return url

    return None


def _cookie_header(jar, url: str) -> str | None:
    request = urllib.request.Request(url)
    jar.add_cookie_header(request)
    header = request.get_header("Cookie")
    return header or None


def _message(status: int, content_type: str, body: bytes) -> str:
    text = message_from_response(content_type, body)

    if text:
        return text

    template = translate("SubtitleCat", "SubtitleCat.com answered HTTP {status}.")
    return template.replace("{status}", str(status))


def _read_capped(response, limit: int) -> bytes:
    data = bytearray()

    while len(data) < limit:
        chunk = response.read(min(65536, limit - len(data)))
        if not chunk:
            break
        data += chunk

    if response.read(1):
        raise SubtitleCatError(
            translate("SubtitleCat", "SubtitleCat.com's answer was too large.")
        )

    return bytes(data)
