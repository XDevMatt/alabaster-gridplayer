from types import SimpleNamespace
from uuid import uuid4

from gridplayer.models.cell_profile import CellProfile
from gridplayer.models.playlist import Playlist
from gridplayer.params.static import AspectFilter
from gridplayer.utils import media_shape
from gridplayer.utils.next_file import ShuffleBag
from gridplayer.widgets.video_block_navigation import NavigationControl


def _fake_nav(mode, portrait_cell):
    block = SimpleNamespace(
        aspect_filter=mode,
        height=lambda: 2160 if portrait_cell else 1080,
        width=lambda: 1080 if portrait_cell else 1920,
    )
    nav = SimpleNamespace(_block=block, ASPECT_PROBE_BUDGET=10)
    nav.cell_is_portrait = lambda: NavigationControl.cell_is_portrait(nav)
    return nav


def _files(tmp_path, shapes):
    files = []
    for i, shape in enumerate(shapes):
        f = tmp_path / f"f{i}.mp4"
        f.write_bytes(b"")
        files.append((f, shape))
    return files


def test_is_portrait():
    assert media_shape.is_portrait(1080, 1920) is True
    assert media_shape.is_portrait(1920, 1080) is False
    assert media_shape.is_portrait(1000, 1000) is False
    assert media_shape.is_portrait(1920, 1080, 5) is True
    assert media_shape.is_portrait(0, 0) is None


def test_shape_is_cached(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(media_shape, "_probe", lambda p: calls.append(p) or True)
    f = tmp_path / "a.mp4"
    f.write_bytes(b"x")
    assert media_shape.shape_of(f) is True
    assert media_shape.shape_of(f) is True
    assert len(calls) == 1


def test_reject_only_gives_matching(tmp_path, monkeypatch):
    files = _files(tmp_path, [True, False, True, False, True, False])
    shapes = dict(files)
    monkeypatch.setattr(media_shape, "shape_of", lambda p: shapes[p])
    nav = _fake_nav(AspectFilter.REJECT, portrait_cell=True)

    bag = ShuffleBag()
    paths = [f for f, _ in files]
    bag.sync("scope", paths, paths[0])
    for _ in range(20):
        fits = NavigationControl._aspect_fits(nav)
        pick = bag.next(exists=fits)
        bag.sync("scope", paths, pick)
        assert shapes[pick] is True


def test_budget_never_gets_stuck(tmp_path, monkeypatch):
    files = _files(tmp_path, [False] * 15)
    monkeypatch.setattr(media_shape, "shape_of", lambda p: False)
    nav = _fake_nav(AspectFilter.REJECT, portrait_cell=True)
    bag = ShuffleBag()
    paths = [f for f, _ in files]
    bag.sync("scope", paths, paths[0])
    assert bag.next(exists=NavigationControl._aspect_fits(nav)) is not None


def test_unknown_counts_as_fit_and_off_means_any(tmp_path, monkeypatch):
    (f, _), = _files(tmp_path, [None])
    monkeypatch.setattr(media_shape, "shape_of", lambda p: None)
    assert NavigationControl._aspect_fits(_fake_nav(AspectFilter.REJECT, False))(f)
    assert NavigationControl._aspect_fits(_fake_nav(AspectFilter.OFF, False)) is None
    assert NavigationControl._aspect_fits(_fake_nav(AspectFilter.ASK, False)) is None


def test_mode_saved_in_cell_profile():
    cell = uuid4()
    text = Playlist(cell_profiles={cell: CellProfile(aspect_filter=AspectFilter.ASK)}).dumps()
    assert Playlist.parse(text).cell_profiles[cell].aspect_filter == AspectFilter.ASK


def test_cache_is_kept_on_disk(tmp_path, monkeypatch):
    cache = tmp_path / "shapes.json"
    monkeypatch.setattr(media_shape, "_cache_file", lambda: cache)
    monkeypatch.setattr(media_shape, "_cache", {})
    monkeypatch.setattr(media_shape, "_loaded", False)
    monkeypatch.setattr(media_shape, "_probe", lambda p: True)
    f = tmp_path / "v.mp4"
    f.write_bytes(b"x")
    assert media_shape.shape_of(f) is True
    assert cache.is_file()

    monkeypatch.setattr(media_shape, "_cache", {})
    monkeypatch.setattr(media_shape, "_loaded", False)
    monkeypatch.setattr(media_shape, "_probe", lambda p: (_ for _ in ()).throw(AssertionError("probed")))
    assert media_shape.shape_of(f) is True


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(media_shape, "_cache_file", lambda: tmp_path / "shapes-default.json")
    monkeypatch.setattr(media_shape, "_cache", {})
    monkeypatch.setattr(media_shape, "_loaded", False)
