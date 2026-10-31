"""0.2beta: snapshots that no longer fit the grid, the aspect filter's
default and [ALL], pictures as slides and the kind of files a cell plays."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from gridplayer.models.cell_profile import CellProfile
from gridplayer.models.grid_state import GridState
from gridplayer.models.playlist import Playlist, Snapshot
from gridplayer.models.video import Video
from gridplayer.params.extensions import SUPPORTED_MEDIA_EXT, is_image_name
from gridplayer.params.static import AspectFilter, MediaKind, VideoEndAction
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.utils.next_file import is_of_kind, of_kind, scan_folder


@pytest.fixture(scope="module")
def qtbot():
    from PyQt5.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _clean_overrides():
    PlaylistSettings().clear()
    yield
    PlaylistSettings().clear()


def _touch(root: Path, *names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")


# --- snapshots -------------------------------------------------------------


class _Blocks(list):
    is_all_initialized = True

    def by_video_id(self, _id):
        return next((b for b in self if str(b.id) == str(_id)), None)

    def blocks_for_ids(self, ids):
        return [b for i in ids if (b := self.by_video_id(i)) is not None]


class _Block:
    def __init__(self, uri):
        self.video_params = Video(uri=uri)
        self.id = self.video_params.id
        self.applied = []

    def apply_snapshot(self, vs):
        self.applied.append(vs)


def _snapshot_manager(qtbot, blocks):
    from gridplayer.player.managers.snapshots import SnapshotsManager

    ctx = SimpleNamespace(
        video_blocks=blocks,
        grid_state=GridState(),
        commands=SimpleNamespace(
            layout_order=lambda: [str(b.id) for b in blocks],
            forget_synced_view=lambda: None,
        ),
    )
    manager = SnapshotsManager(context=ctx)
    warnings, grids = [], []
    manager.warning.connect(warnings.append)
    manager.grid_state_loaded.connect(grids.append)
    return manager, warnings, grids


def test_snapshot_with_a_cell_closed_since_applies_to_the_rest(qtbot):
    blocks = _Blocks([_Block("/v/a.mp4"), _Block("/v/b.mp4")])
    manager, warnings, grids = _snapshot_manager(qtbot, blocks)
    manager.cmd_save_snapshot(1)

    blocks.pop()
    manager.cmd_load_snapshot(1)

    assert len(blocks[0].applied) == 1
    assert warnings == ["Snapshot applied to 1 of 2 cells"]
    assert len(grids) == 1


def test_snapshot_with_a_cell_added_since_leaves_it_alone(qtbot):
    blocks = _Blocks([_Block("/v/a.mp4")])
    manager, warnings, _ = _snapshot_manager(qtbot, blocks)
    manager.cmd_save_snapshot(1)

    blocks.append(_Block("/v/b.mp4"))
    manager.cmd_load_snapshot(1)

    assert len(blocks[0].applied) == 1
    assert blocks[1].applied == []
    assert warnings == ["Snapshot applied to 1 of 2 cells"]


def test_snapshot_of_none_of_the_cells_changes_nothing(qtbot):
    blocks = _Blocks([_Block("/v/a.mp4")])
    manager, warnings, grids = _snapshot_manager(qtbot, blocks)
    manager.set_snapshots(
        {3: Snapshot(grid_state=GridState(), videos=[Video(uri="/v/gone.mp4")])}
    )

    manager.cmd_load_snapshot(3)

    assert blocks[0].applied == []
    assert grids == []
    assert warnings == ["Snapshot applied to 0 of 1 cells"]


def test_full_snapshot_says_nothing(qtbot):
    blocks = _Blocks([_Block("/v/a.mp4"), _Block("/v/b.mp4")])
    manager, warnings, _ = _snapshot_manager(qtbot, blocks)
    manager.cmd_save_snapshot(1)
    manager.cmd_load_snapshot(1)

    assert warnings == []
    assert [len(b.applied) for b in blocks] == [1, 1]


# --- aspect filter default -------------------------------------------------


def test_new_video_takes_the_aspect_filter_default():
    assert Video(uri="/v/a.mp4").aspect_filter == AspectFilter.OFF

    PlaylistSettings().set("video_defaults/aspect_filter", AspectFilter.REJECT)

    assert Video(uri="/v/a.mp4").aspect_filter == AspectFilter.REJECT


def test_playlist_keeps_its_aspect_filter_default_and_old_ones_load():
    playlist = Playlist(video_defaults={"aspect_filter": AspectFilter.ASK})
    again = Playlist.parse(playlist.dumps())
    assert again.video_defaults.aspect_filter == AspectFilter.ASK

    # saved before: no such field on the video nor in the defaults
    assert Video.model_validate({"uri": "/v/a.mp4"}).aspect_filter == (AspectFilter.OFF)
    assert Playlist.parse(Playlist().dumps()).video_defaults.aspect_filter is None


def _block_with_profile(profile):
    from gridplayer.widgets.video_block import VideoBlock

    profiles = {}
    vid = Video(uri="/v/a.mp4")
    if profile is not None:
        profiles[vid.id] = profile

    def set_field(cell_id, name, value):
        base = profiles.get(cell_id) or CellProfile()
        profiles[cell_id] = base.model_copy(update={name: value})

    block = SimpleNamespace(
        video_params=vid,
        _ctx=SimpleNamespace(
            commands=SimpleNamespace(
                cell_profile=lambda cid: profiles.get(cid),
                set_cell_profile_field=set_field,
            )
        ),
    )
    get = lambda: VideoBlock.aspect_filter.fget(block)  # noqa: E731
    set_ = lambda mode: VideoBlock.set_aspect_filter(block, mode)  # noqa: E731
    return block, get, set_, profiles


def test_old_cell_profile_still_wins_until_changed():
    block, get, set_, profiles = _block_with_profile(
        CellProfile(aspect_filter=AspectFilter.ASK)
    )
    assert get() == AspectFilter.ASK

    set_(AspectFilter.REJECT)

    assert get() == AspectFilter.REJECT
    assert profiles[block.video_params.id].aspect_filter is None


def test_per_cell_override_without_profile():
    block, get, set_, _ = _block_with_profile(None)
    assert get() == AspectFilter.OFF
    set_(AspectFilter.ASK)
    assert block.video_params.aspect_filter == AspectFilter.ASK
    assert get() == AspectFilter.ASK


def test_all_videos_aspect_filter_action_wiring():
    from gridplayer.params.actions import ACTIONS
    from gridplayer.params.menu import SECTIONS  # noqa: F401

    for mode in AspectFilter:
        action = ACTIONS[f"Aspect Filter {mode.name} [ALL]"]
        assert action["func"] == ("all", "set_aspect_filter", mode)
        assert action["check_if"] == ("is_all_videos_aspect_filter", mode)
        assert "key" not in action
        assert "keys" not in action


# --- pictures and media kind ----------------------------------------------


@pytest.mark.parametrize(
    "name", ["a.jpg", "A.JPEG", "b.png", "c.webp", "d.gif", "e.bmp", "f.tif", "g.tiff"]
)
def test_pictures_are_known(name):
    assert is_image_name(name)
    assert name.rpartition(".")[2].lower() in SUPPORTED_MEDIA_EXT


@pytest.mark.parametrize("name", ["a.mp4", "b.mkv", "c.mp3", "noext", "x.txt"])
def test_others_are_not_pictures(name):
    assert not is_image_name(name)


def test_kind_filter(tmp_path):
    _touch(tmp_path, "1.mp4", "2.jpg", "3.mkv", "4.png", "5.mp3", "notes.txt")
    scan = scan_folder(tmp_path, is_recursive=False)

    def names(kind):
        return [f.name for f in of_kind(scan, kind).files]

    assert names(MediaKind.ALL) == ["1.mp4", "2.jpg", "3.mkv", "4.png", "5.mp3"]
    assert names(MediaKind.VIDEOS_ONLY) == ["1.mp4", "3.mkv", "5.mp3"]
    assert names(MediaKind.IMAGES_ONLY) == ["2.jpg", "4.png"]
    assert is_of_kind(Path("x.gif"), MediaKind.IMAGES_ONLY)


def test_stepping_with_kind_wraps_and_skips(tmp_path):
    _touch(tmp_path, "1.mp4", "2.jpg", "3.mkv", "4.png")
    scan = scan_folder(tmp_path, is_recursive=False)

    videos = of_kind(scan, MediaKind.VIDEOS_ONLY)
    images = of_kind(scan, MediaKind.IMAGES_ONLY)

    assert videos.neighbour(tmp_path / "1.mp4", 1) == tmp_path / "3.mkv"
    # the last one goes round to the first
    assert videos.neighbour(tmp_path / "3.mkv", 1) == tmp_path / "1.mp4"
    # from a video, Next in Images only goes to the picture after it
    assert images.neighbour(tmp_path / "1.mp4", 1) == tmp_path / "2.jpg"
    assert images.neighbour(tmp_path / "4.png", 1) == tmp_path / "2.jpg"
    assert images.neighbour(tmp_path / "2.jpg", -1) == tmp_path / "4.png"


def test_next_wraps_round_with_subfolders(tmp_path):
    _touch(tmp_path, "a.mp4", "sub/b.mp4", "sub/c.mp4")
    scan = scan_folder(tmp_path, is_recursive=True)

    assert scan.neighbour(tmp_path / "sub/c.mp4", 1) == tmp_path / "a.mp4"
    assert scan.neighbour(tmp_path / "a.mp4", -1) == tmp_path / "sub/c.mp4"


def test_slide_duration_and_kind_defaults():
    video = Video(uri="/v/a.png")
    assert video.media_kind == MediaKind.VIDEOS_ONLY
    assert video.slide_duration_sec == 10

    PlaylistSettings().set("video_defaults/slide_duration", 4)
    PlaylistSettings().set("video_defaults/media_kind", MediaKind.IMAGES_ONLY)
    video = Video(uri="/v/a.png")
    assert video.slide_duration_sec == 4
    assert video.media_kind == MediaKind.IMAGES_ONLY


def test_slide_end_runs_when_finished():
    """A slide's end is a video's end: VLC reports the picture as a clip
    of the slide duration, and the cell's time passing its end runs its
    When Finished."""

    from gridplayer.widgets.video_block import VideoBlock

    steps = []
    video = Video(uri="/v/a.png", end_action=VideoEndAction.NEXT_FILE)
    block = SimpleNamespace(
        video_params=video,
        _hold_end_for_bookmarks=lambda: False,
        navigation=SimpleNamespace(
            next=lambda is_end: steps.append(is_end),
            previous=None,
            shuffle=None,
        ),
    )
    block._step_at_end = lambda action: VideoBlock._step_at_end(block, action)

    VideoBlock.loop_end_action(block)

    assert steps == [True]
