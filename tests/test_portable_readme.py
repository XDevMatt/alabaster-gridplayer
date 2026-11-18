"""The portable zip's README must point at this repo's default branch."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "scripts" / "windows" / "PORTABLE-README.txt"
SOURCE = "https://github.com/XDevMatt/alabaster-gridplayer/tree/main"


def test_portable_readme_points_at_main():
    text = README.read_text(encoding="utf-8")

    assert SOURCE in text
    assert "0.2beta-fixes" not in text
    assert "XDevMatt/alabaster-gridplayer" in text
