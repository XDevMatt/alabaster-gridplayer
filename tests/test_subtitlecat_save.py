"""Subtitles are saved beside the video, or under the data folder."""

from pathlib import Path

import pytest

from gridplayer.plugins.subtitlecat.save import (
    SaveError,
    folder_is_writable,
    save_bytes,
    subtitle_folder,
)


def test_a_local_video_gets_the_file_beside_it(tmp_path):
    video = tmp_path / "clip.mkv"
    video.write_bytes(b"v")

    folder = subtitle_folder(video, data_dir=tmp_path / "data")
    path = save_bytes(folder, "Britains.srt", b"1\n")

    assert folder == tmp_path
    assert path == tmp_path / "Britains.srt"
    assert path.read_bytes() == b"1\n"
    assert list(tmp_path.glob(".gp-subtitle-probe-*")) == []


def test_an_existing_file_is_not_overwritten(tmp_path):
    (tmp_path / "A.srt").write_bytes(b"old")

    path = save_bytes(tmp_path, "A.srt", b"new")

    assert path.name == "A-2.srt"
    assert path.read_bytes() == b"new"
    assert (tmp_path / "A.srt").read_bytes() == b"old"


def test_a_missing_video_folder_uses_the_data_subtitles_dir(tmp_path):
    video = tmp_path / "missing" / "clip.mkv"
    data = tmp_path / "data"

    folder = subtitle_folder(video, data_dir=data)

    assert folder == data / "subtitles"
    assert folder.is_dir()


def test_a_remote_video_uses_the_data_folder(tmp_path):
    data = tmp_path / "data"

    folder = subtitle_folder("https://example.com/a.mkv", data_dir=data)

    assert folder == data / "subtitles"


def test_a_relative_path_uses_the_data_folder(tmp_path):
    folder = subtitle_folder(Path("clip.mkv"), data_dir=tmp_path / "data")

    assert folder == tmp_path / "data" / "subtitles"


def test_nowhere_writable_is_an_error(tmp_path):
    blocked = tmp_path / "not-a-dir"
    blocked.write_text("x", encoding="utf-8")
    video = tmp_path / "missing" / "clip.mkv"

    with pytest.raises(SaveError):
        subtitle_folder(video, data_dir=blocked)


def test_a_file_is_not_a_writable_folder(tmp_path):
    blocked = tmp_path / "file"
    blocked.write_bytes(b"x")

    assert folder_is_writable(blocked) is False


def test_a_name_with_a_slash_is_refused(tmp_path):
    with pytest.raises(SaveError):
        save_bytes(tmp_path, "a/b.srt", b"1\n")
