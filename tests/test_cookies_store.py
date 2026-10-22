"""The stored jar is gone. A leftover cookies.txt is left on disk unused."""

from gridplayer.utils import cookies as cookies_module
from gridplayer.utils.cookies import leftover_cookie_file, ytdl_cookies


def test_a_leftover_file_is_not_read_or_deleted(tmp_path, monkeypatch):
    monkeypatch.setattr(cookies_module, "get_app_data_dir", lambda: tmp_path)
    path = leftover_cookie_file()
    path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

    with ytdl_cookies() as opts:
        assert opts == {}

    assert path.exists()
    assert not hasattr(cookies_module, "CookieStore")
    assert not hasattr(cookies_module, "parse_cookies")
