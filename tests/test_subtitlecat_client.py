"""SubtitleCat requests: a session, one at a time, nothing written down."""

import http.cookiejar
import logging
import os
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from gridplayer.params.static import ProxyMode
from gridplayer.plugins.subtitlecat.client import (
    DEFAULT_TIMEOUT_SEC,
    TRANSLATE_URL,
    DownloadOutcome,
    EmptySearch,
    HostRedirectHandler,
    NoSession,
    PluginOff,
    PoliteGate,
    SubtitleCatClient,
    SubtitleCatError,
    TimedOut,
    TranslateOff,
    _opener,
)
from gridplayer.plugins.subtitlecat.parse import TranslateRequest
from gridplayer.plugins.subtitlecat.session import (
    _QuietLogger,
    read_for_request,
    take_subtitlecat_cookies,
)
from gridplayer.utils.network import NetworkOpts

VIP = (
    "You are out of free translations. You can either wait one hour, "
    "or sign up to a VIP account for unlimited translations!"
)
SECRET = "secret-cookie"
FIXTURES = Path(__file__).parent / "fixtures" / "subtitlecat"


def _cookie(name, value, domain=".subtitlecat.com"):
    return http.cookiejar.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=domain.startswith("."),
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
    )


def make_jar(*cookies):
    jar = http.cookiejar.CookieJar()
    for cookie in cookies:
        jar.set_cookie(cookie)
    return jar


def _settings(**overrides):
    values = {
        "plugins/subtitlecat": True,
        "plugins/subtitlecat_translate": False,
    }
    values.update(overrides)

    def get(key):
        return values[key]

    return get


class _Clock:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


class _Response:
    def __init__(self, body, status=200, content_type="text/html"):
        self.status = status
        self.code = status
        self.headers = {"Content-Type": content_type}
        self._body = body

    def read(self, _size=-1):
        body, self._body = self._body, b""
        return body

    def close(self):
        return None


def _client(transport, jar=None, logged_in=True, browser="chrome", **settings):
    if jar is None:
        jar = make_jar(_cookie("PHPSESSID", SECRET))

    def session():
        return jar, logged_in, browser

    clock = _Clock()
    return (
        SubtitleCatClient(
            settings_get=_settings(**settings),
            session=session,
            transport=transport,
            gate=PoliteGate(min_gap=1, clock=clock, sleep=clock.sleep),
            user_agent="TestAgent",
        ),
        jar,
        clock,
    )


def test_plugin_off_does_not_read_a_session_or_fetch():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client = SubtitleCatClient(
        settings_get=_settings(**{"plugins/subtitlecat": False}),
        session=refuse,
        transport=refuse,
    )

    with pytest.raises(PluginOff):
        client.search("Sintel")


def test_an_empty_search_does_not_fetch():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client, _jar, _clock = _client(refuse)

    with pytest.raises(EmptySearch):
        client.search("  ")


def test_no_session_means_no_request():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client, _jar, _clock = _client(
        refuse, jar=make_jar(), logged_in=False, browser="firefox"
    )

    with pytest.raises(NoSession, match="Firefox"):
        client.search("Sintel")


def test_no_browser_means_no_request_and_says_to_choose_one():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client, _jar, _clock = _client(refuse, jar=make_jar(), logged_in=False, browser="")

    with pytest.raises(NoSession, match="Choose a browser"):
        client.search("Sintel")


def test_translate_off_does_not_fetch():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client, _jar, _clock = _client(refuse)
    request = TranslateRequest("sq", "A.srt", "/subs/1/")

    with pytest.raises(TranslateOff):
        client.translate(request, "https://www.subtitlecat.com/subs/1/A.html")


def test_a_search_sends_the_session_once_and_forgets_it(caplog):
    caplog.set_level(logging.DEBUG)
    calls = []
    html = (FIXTURES / "search-sintel.html").read_bytes()

    def transport(method, url, headers, data, timeout, limit):
        calls.append((method, url, dict(headers), data, timeout, limit))
        return 200, "text/html", html

    jar = make_jar(_cookie("PHPSESSID", SECRET), _cookie("cf_clearance", "cf-value"))
    client, jar, clock = _client(transport, jar=jar)
    outcome = client.search("Sintel")

    assert [hit.title for hit in outcome.hits][:1] == ["Sintel (2010)"]
    assert len(calls) == 1
    method, url, headers, data, timeout, _limit = calls[0]
    assert method == "GET"
    assert url == "https://www.subtitlecat.com/index.php?search=Sintel"
    assert headers["User-Agent"] == "TestAgent"
    assert headers["Referer"] == "https://www.subtitlecat.com/"
    assert "Accept-Language" not in headers
    assert SECRET in headers["Cookie"]
    assert "cf-value" in headers["Cookie"]
    assert data is None
    assert timeout == DEFAULT_TIMEOUT_SEC
    assert list(jar) == []
    assert SECRET not in caplog.text
    assert clock.slept == []

    client.search("Sintel")
    assert clock.slept == [1]


def test_requests_do_not_overlap():
    gate = PoliteGate(min_gap=0, clock=lambda: 0, sleep=lambda _seconds: None)
    order = []

    def work(number):
        def inner():
            order.append(("start", number))
            threading.Event().wait(0.05)
            order.append(("end", number))

        gate.run(inner)

    threads = [threading.Thread(target=work, args=(number,)) for number in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert order in (
        [("start", 1), ("end", 1), ("start", 2), ("end", 2)],
        [("start", 2), ("end", 2), ("start", 1), ("end", 1)],
    )


def test_an_off_site_redirect_is_refused_before_a_new_request():
    handler = HostRedirectHandler()
    request = urllib.request.Request("https://www.subtitlecat.com/index.php")
    request.add_header("Cookie", "PHPSESSID=" + SECRET)

    with pytest.raises(SubtitleCatError):
        handler.redirect_request(
            request, None, 302, "Found", {}, "https://evil.example/steal"
        )


def test_an_on_site_redirect_is_allowed():
    handler = HostRedirectHandler()
    request = urllib.request.Request("https://www.subtitlecat.com/index.php")
    redirected = handler.redirect_request(
        request,
        None,
        302,
        "Found",
        {},
        "https://subtitlecat.com/subs/1/A.html",
    )

    assert redirected.get_full_url() == "https://subtitlecat.com/subs/1/A.html"


def test_a_limit_page_is_shown_as_sent_and_not_retried():
    html = (FIXTURES / "limit-message.html").read_bytes()
    calls = []

    def transport(method, url, headers, data, timeout, limit):
        calls.append(url)
        return 429, "text/html", html

    client, _jar, _clock = _client(transport, **{"plugins/subtitlecat_translate": True})
    request = TranslateRequest("sq", "Sintel (2010).eng-orig.srt", "/subs/751/")
    page = "https://www.subtitlecat.com/subs/751/Sintel.html"
    outcome = client.translate(request, page)

    assert outcome.text == VIP
    assert outcome.download_url is None
    assert calls == [TRANSLATE_URL]
    assert SECRET not in outcome.text


def test_translate_posts_the_file_identity_and_not_the_subtitle(caplog):
    caplog.set_level(logging.DEBUG)
    calls = []
    raw = b'{"file": "https://www.subtitlecat.com/subs/751/A.srt"}'

    def transport(method, url, headers, data, timeout, limit):
        calls.append((method, url, dict(headers), data))
        return 200, "application/json", raw

    client, jar, _clock = _client(transport, **{"plugins/subtitlecat_translate": True})
    page = "https://www.subtitlecat.com/subs/751/Sintel.html"
    outcome = client.translate(
        TranslateRequest("sq", "Sintel (2010).eng-orig.srt", "/subs/751/"),
        page,
    )

    assert len(calls) == 1
    method, url, headers, data = calls[0]
    body = data.decode("ascii")
    assert method == "POST"
    assert url == TRANSLATE_URL
    assert headers["Referer"] == page
    assert "to_language=sq" in body
    assert "folder=%2Fsubs%2F751%2F" in body
    assert "content=" not in body
    assert outcome.download_url == "https://www.subtitlecat.com/subs/751/A.srt"
    assert outcome.body is None
    assert list(jar) == []
    assert SECRET not in caplog.text


def test_html_is_not_saved_as_a_subtitle():
    def transport(method, url, headers, data, timeout, limit):
        return 200, "text/html", b"<html><body>Sign in</body></html>"

    client, _jar, _clock = _client(transport)
    outcome = client.download(
        "https://www.subtitlecat.com/subs/1/A.srt",
        "https://www.subtitlecat.com/subs/1/A.html",
    )

    assert outcome.kind == "message"
    assert outcome.body == b""
    assert outcome.message == "Sign in"


def test_a_subtitle_download_keeps_the_bytes():
    payload = b"1\n00:00:00,000 --> 00:00:01,000\nHi\n"

    def transport(method, url, headers, data, timeout, limit):
        assert "example.com" not in url
        return 200, "application/octet-stream", payload

    client, _jar, _clock = _client(transport)
    outcome = client.download(
        "https://www.subtitlecat.com/subs/1/Britain%27s.srt",
        "https://www.subtitlecat.com/subs/1/A.html",
    )

    assert isinstance(outcome, DownloadOutcome)
    assert outcome.kind == "subtitle"
    assert outcome.body == payload
    assert outcome.filename == "Britains.srt"


def test_an_off_site_download_is_refused_without_a_session():
    def refuse(*_args, **_kwargs):
        raise AssertionError("called")

    client = SubtitleCatClient(
        settings_get=_settings(),
        session=refuse,
        transport=refuse,
    )

    with pytest.raises(SubtitleCatError, match="not on SubtitleCat"):
        client.download("https://evil.example/a.srt", "https://evil.example/")


def test_a_foreign_referer_is_not_sent():
    calls = []

    def transport(method, url, headers, data, timeout, limit):
        calls.append(headers)
        return 200, "text/html", (FIXTURES / "page-sintel.html").read_bytes()

    client, _jar, _clock = _client(transport)
    client.page(
        "https://www.subtitlecat.com/subs/751/A.html",
        "https://evil.example/from",
    )

    assert "Referer" not in calls[0]


def test_a_timeout_is_a_clear_error(monkeypatch):
    def open_timeout(self, request, timeout=None):
        raise TimeoutError("timed out")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", open_timeout)
    jar = make_jar(_cookie("PHPSESSID", SECRET))
    client = SubtitleCatClient(
        settings_get=_settings(),
        session=lambda: (jar, True, "chrome"),
        opts=_opts(),
        user_agent="TestAgent",
        gate=PoliteGate(min_gap=0, clock=lambda: 0, sleep=lambda _seconds: None),
    )

    with pytest.raises(TimedOut, match="did not answer in time"):
        client.search("Sintel")


def test_a_network_error_does_not_include_the_url_or_the_cookie(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    def open_fail(self, request, timeout=None):
        raise urllib.error.URLError("https://www.subtitlecat.com/?token=" + SECRET)

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", open_fail)
    jar = make_jar(_cookie("PHPSESSID", SECRET))
    client = SubtitleCatClient(
        settings_get=_settings(),
        session=lambda: (jar, True, "chrome"),
        opts=_opts(),
        user_agent="TestAgent",
        gate=PoliteGate(min_gap=0, clock=lambda: 0, sleep=lambda _seconds: None),
    )

    with pytest.raises(SubtitleCatError, match="could not be reached") as raised:
        client.search("Sintel")

    assert SECRET not in str(raised.value)
    assert SECRET not in caplog.text


def test_a_search_does_not_write_a_file(monkeypatch):
    def transport(method, url, headers, data, timeout, limit):
        return 200, "text/html", b"<html></html>"

    def refuse(self, *_args, **_kwargs):
        raise AssertionError(self)

    monkeypatch.setattr(Path, "write_bytes", refuse)
    monkeypatch.setattr(Path, "write_text", refuse)
    client, _jar, _clock = _client(transport)
    client.search("Sintel")


def test_only_subtitlecat_cookies_count_as_a_session():
    source = make_jar(
        _cookie("PHPSESSID", SECRET),
        _cookie("cf_clearance", "cf-value"),
        _cookie("_ga", "analytics", domain=".subtitlecat.com"),
        _cookie("PHPSESSID", "other", domain="evilsubtitlecat.com"),
        _cookie("sid", "nope", domain="notsubtitlecat.com"),
    )
    kept, logged_in = take_subtitlecat_cookies(source)

    names = sorted(cookie.name for cookie in kept)
    assert logged_in is True
    assert names == ["PHPSESSID", "_ga", "cf_clearance"]
    assert all(cookie.value != "other" and cookie.value != "nope" for cookie in kept)


def test_cloudflare_alone_is_not_a_session():
    kept, logged_in = take_subtitlecat_cookies(
        make_jar(_cookie("cf_clearance", "cf-value"), _cookie("_ga", "analytics"))
    )

    assert logged_in is False
    assert len(list(kept)) == 2


def test_the_reader_is_not_called_without_a_browser(monkeypatch):
    monkeypatch.setattr(
        "gridplayer.plugins.subtitlecat.session.Settings",
        lambda: _BrowserStore(""),
    )

    def refuse(*_args, **_kwargs):
        raise AssertionError("reader")

    jar, logged_in, browser = read_for_request(refuse)

    assert logged_in is False
    assert browser == ""
    assert list(jar) == []


def test_the_yt_dlp_reader_gets_a_quiet_logger(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    seen = {}

    class Recording(http.cookiejar.CookieJar):
        def __init__(self):
            super().__init__()
            self.saved = False

        def save(self, *_args, **_kwargs):
            self.saved = True

    source = Recording()
    source.set_cookie(_cookie("PHPSESSID", SECRET))

    def fake(browser_name, profile=None, logger=None, **_kwargs):
        seen["browser"] = browser_name
        seen["profile"] = profile
        seen["logger"] = logger
        logger.warning("token=" + SECRET)
        logger.debug("token=" + SECRET)
        return source

    monkeypatch.setattr("yt_dlp.cookies.extract_cookies_from_browser", fake)
    monkeypatch.setattr(
        "gridplayer.plugins.subtitlecat.session.Settings",
        lambda: _BrowserStore("firefox", "dev"),
    )

    jar, logged_in, browser = read_for_request()

    assert seen == {
        "browser": "firefox",
        "profile": "dev",
        "logger": seen["logger"],
    }
    assert isinstance(seen["logger"], _QuietLogger)
    assert logged_in is True
    assert browser == "firefox"
    assert [cookie.value for cookie in jar] == [SECRET]
    assert source.saved is False
    assert list(source) == []
    assert SECRET not in caplog.text


def test_the_package_does_not_name_a_workaround():
    root = Path(__file__).resolve().parents[1] / "gridplayer" / "plugins"
    text = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py"))

    for banned in (
        "translate.googleapis.com",
        "upload_subtitles",
        "upload_private_subtitles",
        "get_shared_translation",
        "visitor_log",
    ):
        assert banned not in text


def test_force_ipv4_is_a_connection_handler_not_a_listener():
    opener = _opener(_opts(force_ipv4=True))
    names = {type(handler).__name__ for handler in opener.handlers}

    assert "_IPv4HTTPHandler" in names
    assert "_IPv4HTTPSHandler" in names


def test_no_proxy_installs_no_proxy_and_a_custom_one_is_used():
    # An empty ProxyHandler is what "no proxy" is. urllib then skips the
    # machine's proxy handler, and the empty one adds no address.
    direct = _opener(_opts(proxy_mode=ProxyMode.NONE))
    custom = _opener(_opts(proxy_mode=ProxyMode.CUSTOM, proxy="http://127.0.0.1:9"))

    assert _proxy_maps(direct) == []
    assert _proxy_maps(custom) == [
        {"http": "http://127.0.0.1:9", "https": "http://127.0.0.1:9"}
    ]


def _proxy_maps(opener):
    return [
        dict(handler.proxies)
        for handler in opener.handlers
        if getattr(handler, "proxies", None)
    ]


@pytest.mark.skipif(
    os.environ.get("GRIDPLAYER_SUBTITLECAT_LIVE") != "1",
    reason="set GRIDPLAYER_SUBTITLECAT_LIVE=1 to search SubtitleCat",
)
def test_live_sintel_or_no_session():
    client = SubtitleCatClient()

    try:
        outcome = client.search("Sintel")
    except NoSession:
        return

    assert outcome.hits or outcome.message


class _BrowserStore:
    def __init__(self, browser, profile=""):
        self._values = {
            "cookies/from_browser": browser,
            "cookies/browser_profile": profile,
        }
        self.writes = []

    def get(self, key):
        return self._values[key]

    def set(self, *_args):
        self.writes.append(_args)
        raise AssertionError("settings written")


def _opts(**overrides):
    values = {
        "proxy_mode": ProxyMode.NONE,
        "proxy": "",
        "user_agent": "TestAgent",
        "force_ipv4": False,
        "timeout": 0,
        "verify_tls": True,
    }
    values.update(overrides)
    return NetworkOpts(**values)
