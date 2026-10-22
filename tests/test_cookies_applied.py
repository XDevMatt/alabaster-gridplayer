"""yt-dlp gets browser cookies in memory, never a stored jar."""

from gridplayer.utils import cookies as cookies_module
from gridplayer.utils.cookies import leftover_cookie_file, ytdl_cookies
from gridplayer.utils.url_resolve.resolver_base import DirectResolver
from tests.conftest import FakeSettings


def test_ytdl_cookies_are_empty_by_default(monkeypatch):
    monkeypatch.setattr(
        cookies_module, "Settings", lambda: FakeSettings({"cookies/from_browser": ""})
    )

    with ytdl_cookies() as opts:
        assert opts == {}


def test_ytdl_cookies_pass_the_browser_flag(monkeypatch):
    monkeypatch.setattr(
        cookies_module,
        "Settings",
        lambda: FakeSettings(
            {"cookies/from_browser": "firefox", "cookies/browser_profile": "dev"}
        ),
    )

    with ytdl_cookies() as opts:
        assert opts == {"cookiesfrombrowser": ("firefox", "dev", None, None)}


def test_leftover_cookie_file_is_not_read(tmp_path, monkeypatch):
    jar = tmp_path / "cookies.txt"
    jar.write_text(
        "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tFALSE\t0\tSID\tx\n"
    )
    monkeypatch.setattr(cookies_module, "get_app_data_dir", lambda: tmp_path)

    assert leftover_cookie_file() == jar
    assert jar.exists()

    with ytdl_cookies() as opts:
        assert "cookiefile" not in opts


def test_direct_urls_are_never_proxied_for_cookies():
    stream = DirectResolver("https://www.youtube.com/v.mp4").streams["generic"]

    assert stream.protocol == "direct"


def test_has_cookies_for_is_always_false():
    assert not cookies_module.has_cookies_for("https://www.youtube.com/")
