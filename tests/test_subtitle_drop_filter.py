"""Subtitle files dropped on a cell must not be filtered out first."""

from pathlib import Path

import pytest
from PyQt5.QtCore import QMimeData, QUrl
from PyQt5.QtWidgets import QApplication

from gridplayer.utils.files import extract_mime_uris, is_subtitle_file_name


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _urls(*paths: Path) -> QMimeData:
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path)) for path in paths])
    return mime


def test_an_srt_is_a_subtitle_file():
    assert is_subtitle_file_name("movie.en.srt")
    assert is_subtitle_file_name("movie.VTT")
    assert not is_subtitle_file_name("movie.mp4")
    assert not is_subtitle_file_name("movie")


def test_a_drop_of_only_media_is_unchanged(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"")

    assert extract_mime_uris(_urls(video)) == [str(video)]
    assert extract_mime_uris(_urls(video), with_subtitles=True) == [str(video)]


def test_a_subtitle_file_is_kept_only_when_asked(tmp_path):
    subtitle = tmp_path / "clip.srt"
    subtitle.write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n")

    assert extract_mime_uris(_urls(subtitle)) == []
    assert extract_mime_uris(_urls(subtitle), with_subtitles=True) == [str(subtitle)]


def test_a_subtitle_beside_a_video_is_kept_when_asked(tmp_path):
    video = tmp_path / "clip.mp4"
    subtitle = tmp_path / "clip.srt"
    video.write_bytes(b"")
    subtitle.write_text("1\n")

    both = _urls(video, subtitle)
    assert extract_mime_uris(both) == [str(video)]
    assert extract_mime_uris(both, with_subtitles=True) == [str(video), str(subtitle)]
