"""Dropped files go through the same extension list as folder scans."""

import pytest

from gridplayer.params.extensions import SUPPORTED_MEDIA_EXT, SUPPORTED_VIDEO_EXT
from gridplayer.utils.files import _is_known_file_name

KEPT = (
    "asf avi divx flv m4v mkv mov mp4 mp4v mpeg mpg webm wmv ts m2ts mts 3gp ogv rmvb"
)


@pytest.mark.parametrize("ext", KEPT.split())
def test_real_video_types_stay(ext):
    assert ext in SUPPORTED_VIDEO_EXT


@pytest.mark.parametrize("ext", "iso vob ifo vro evo bdmv mpls asx".split())
def test_disc_images_indexes_and_playlists_are_not_media(ext):
    assert ext not in SUPPORTED_MEDIA_EXT
    assert not _is_known_file_name(f"a.{ext}")
