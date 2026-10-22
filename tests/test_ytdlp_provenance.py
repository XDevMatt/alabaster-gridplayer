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
