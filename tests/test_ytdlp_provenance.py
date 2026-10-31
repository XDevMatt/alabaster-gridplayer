from gridplayer.utils import ytdlp_provenance as provenance
from tests.conftest import FakeSettings


def test_bundled_module_is_yt_dlp():
    assert provenance.bundled_module_name() == "yt_dlp"


def test_external_binary_is_off_by_default(monkeypatch):
    monkeypatch.setattr(
        provenance,
        "Settings",
        lambda: FakeSettings({"streaming/ytdlp_external_path": ""}),
    )

    assert provenance.external_binary() is None


def test_path_is_not_searched(monkeypatch, tmp_path):
    fake = tmp_path / "yt-dlp.exe"
    fake.write_bytes(b"")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setattr(
        provenance,
        "Settings",
        lambda: FakeSettings({"streaming/ytdlp_external_path": ""}),
    )

    assert provenance.external_binary() is None


def test_opt_in_uses_the_chosen_file(monkeypatch, tmp_path):
    binary = tmp_path / "my-yt-dlp.exe"
    binary.write_bytes(b"")
    monkeypatch.setattr(
        provenance,
        "Settings",
        lambda: FakeSettings({"streaming/ytdlp_external_path": str(binary)}),
    )

    assert provenance.external_binary() == binary


def test_a_bare_name_is_looked_up_on_path(monkeypatch, tmp_path):
    binary = tmp_path / "yt-dlp"
    monkeypatch.setattr(provenance.shutil, "which", lambda name: str(binary))

    assert provenance.external_binary("yt-dlp") == binary


def test_a_missing_file_falls_back_to_the_module(monkeypatch, tmp_path):
    monkeypatch.setattr(provenance.shutil, "which", lambda name: None)

    assert provenance.external_binary(str(tmp_path / "nope" / "yt-dlp")) is None
    assert provenance.external_binary("yt-dlp") is None


def test_options_become_flags():
    args = provenance.cli_args(
        {
            "noplaylist": True,
            "extract_flat": "in_playlist",
            "playlistend": 50,
            "cookiesfrombrowser": ("firefox", None, None, None),
            "js_runtimes": {"deno": {"path": "/opt/deno"}},
            "http_headers": {"User-Agent": "x"},
        }
    )

    assert "--no-playlist" in args
    assert "--flat-playlist" in args
    assert args[args.index("--playlist-end") + 1] == "50"
    assert args[args.index("--cookies-from-browser") + 1] == "firefox"
    assert args[args.index("--js-runtimes") + 1] == "deno:/opt/deno"
    assert args[args.index("--add-header") + 1] == "User-Agent:x"


def test_the_resolver_runs_the_chosen_program(monkeypatch, tmp_path):
    """The setting is what picks the yt-dlp a link is resolved with."""

    from gridplayer.utils.url_resolve import resolver_yt_dlp

    binary = tmp_path / "yt-dlp"
    binary.write_bytes(b"")
    monkeypatch.setattr(resolver_yt_dlp, "external_binary", lambda: binary)
    monkeypatch.setattr(resolver_yt_dlp, "ytdl_js_runtimes", dict)
    monkeypatch.setattr(resolver_yt_dlp, "ytdl_network_opts", dict)

    ran = []

    def fake_run(command, **_kwargs):
        ran.append(command)
        return provenance.subprocess.CompletedProcess(
            command, 0, stdout='{"id": "abc", "title": "t"}', stderr=""
        )

    monkeypatch.setattr(provenance.subprocess, "run", fake_run)

    resolver = resolver_yt_dlp.YoutubeDLResolver.__new__(
        resolver_yt_dlp.YoutubeDLResolver
    )
    resolver.url = "https://example.com/v"
    resolver.headers = None
    resolver.progress = None
    resolver._log = __import__("logging").getLogger("test")

    assert resolver._video_info["id"] == "abc"
    assert ran[0][0] == str(binary)
    assert ran[0][-1] == "https://example.com/v"
