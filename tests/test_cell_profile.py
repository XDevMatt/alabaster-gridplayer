from pathlib import Path
from uuid import uuid4

from gridplayer.models.cell_profile import CellProfile, CellSource, effective
from gridplayer.models.playlist import Playlist
from gridplayer.models.video import Video
from gridplayer.params.static import VideoEndAction


def _videos(where):
    videos = []
    for name in ("a.mp4", "b.mp4"):
        (where / name).write_bytes(b"")
        videos.append(Video(uri=where / name))
    return videos


def test_round_trip_keeps_ids_and_profiles(tmp_path):
    videos = _videos(tmp_path)
    profiles = {
        videos[0].id: CellProfile(
            sources=[CellSource(path=Path("C:/clips"), weight=2.0)],
            upscale="lanczos",
            downscale="area",
            deband=True,
            end_action=VideoEndAction.SHUFFLE_FILE,
            loop=False,
        ),
        videos[1].id: CellProfile(deband=False),
    }
    text = Playlist(videos=videos, cell_profiles=profiles).dumps()
    back = Playlist.parse(text)

    assert [v.id for v in back.videos] == [v.id for v in videos]
    assert back.cell_profiles == profiles


def test_old_playlist_without_profiles_loads(tmp_path):
    text = Playlist(videos=_videos(tmp_path)).dumps()
    assert "cell_profiles" not in text
    back = Playlist.parse(text)
    assert back.cell_profiles is None
    assert len(back.videos) == 2


def test_settings_are_defaults_cell_overrides():
    assert effective(CellProfile(), "deband", False) is False
    assert effective(CellProfile(deband=True), "deband", False) is True
    assert effective(None, "upscale", "bicubic") == "bicubic"
    assert effective(CellProfile(upscale="lanczos"), "upscale", "bicubic") == "lanczos"


def test_profile_for_unknown_key_is_ignored_safely():
    back = Playlist.parse(
        '{"format": "gridplayer-playlist", "version": 1, "cell_profiles": {"%s": {"loop": true}}}'
        % uuid4()
    )
    assert list(back.cell_profiles.values()) == [CellProfile(loop=True)]
