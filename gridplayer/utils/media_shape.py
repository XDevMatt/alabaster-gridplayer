"""Whether a file is portrait or landscape, as VLC reads it, in a process
of its own (as FileLengths does) and remembered per file."""

import json
import logging
import threading
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path

_log = logging.getLogger(__name__)

PARSE_TIMEOUT_MS = 3000

# (path, mtime_ns, size) -> True portrait, False landscape, None unknown
_cache: dict[tuple, bool | None] = {}
_loaded = False
CACHE_FILE_NAME = "media_shapes.json"


def _cache_file() -> Path:
    from gridplayer.utils.app_dir import get_app_data_dir

    return get_app_data_dir() / CACHE_FILE_NAME


def _load() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        rows = json.loads(_cache_file().read_text(encoding="utf-8"))
        for path, mtime, size, shape in rows:
            _cache.setdefault((path, mtime, size), shape)
    except (OSError, ValueError, TypeError):
        pass


def _save() -> None:
    try:
        rows = [[*key, shape] for key, shape in _cache.items()]
        target = _cache_file()
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows), encoding="utf-8")
        tmp.replace(target)
    except OSError as e:
        _log.warning(f"File shapes not saved: {e}")
_pool: ProcessPoolExecutor | None = None
_lock = threading.Lock()


def is_portrait(width: int, height: int, orientation: int = 0) -> bool | None:
    """Square counts as landscape; VLC orientations 4..7 are rotated 90."""

    if not width or not height:
        return None
    if orientation >= 4:
        width, height = height, width
    return height > width


def _key(path: Path):
    try:
        st = path.stat()
    except OSError:
        return None
    return (str(path), st.st_mtime_ns, st.st_size)


def shape_of(path: Path) -> bool | None:
    key = _key(path)
    if key is None:
        return None
    _load()
    if key in _cache:
        return _cache[key]
    shape = _probe(path)
    _cache[key] = shape
    if shape is not None:
        _save()
    return shape


def _probe(path: Path) -> bool | None:
    global _pool
    with _lock:
        if _pool is None:
            _pool = ProcessPoolExecutor(
                max_workers=1,
                mp_context=get_context("spawn"),
                initializer=_exit_with_parent,
            )
            _release_on_quit()
        pool = _pool
    try:
        return pool.submit(shapes_in_process, [str(path)]).result()[0]
    except Exception as e:
        _log.warning(f"File shape not read: {e}")
        with _lock:
            _pool = None
        pool.shutdown(wait=False, cancel_futures=True)
        return None


def _exit_with_parent() -> None:
    """In the probing process: end when the app is gone, however it went
    (the app may leave with os._exit, which runs no clean-up)."""

    import multiprocessing
    import os
    import time

    parent = multiprocessing.parent_process()
    if parent is None:
        return

    def watch():
        while parent.is_alive():
            time.sleep(1)
        os._exit(0)

    threading.Thread(target=watch, daemon=True).start()


def release() -> None:
    """Let the probing process go, so the app can exit."""

    global _pool
    with _lock:
        pool, _pool = _pool, None
    if pool is not None:
        pool.shutdown(wait=False, cancel_futures=True)


def _release_on_quit() -> None:
    try:
        from PyQt5.QtCore import QCoreApplication

        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(release)
    except Exception:
        pass


_vlc_instance = None

def shapes_in_process(paths: list[str]) -> list[bool | None]:
    global _vlc_instance
    import time

    from gridplayer.vlc_player.libvlc import vlc

    if _vlc_instance is None:
        _vlc_instance = vlc.Instance(
            ["--intf=dummy", "--quiet", "--no-video", "--no-audio", "--no-lua",
             "--no-interact", "--no-sub-autodetect-file"]
        )

    out = []
    for path in paths:
        media = _vlc_instance.media_new_path(path)
        try:
            media.parse_with_options(vlc.MediaParseFlag.local, PARSE_TIMEOUT_MS)
            deadline = time.monotonic() + PARSE_TIMEOUT_MS / 1000 + 1
            while time.monotonic() < deadline:
                status = getattr(media.get_parsed_status(), "value", media.get_parsed_status())
                if status in (1, 2, 3, 4):
                    break
                time.sleep(0.005)
            shape = None
            for track in media.tracks_get() or ():
                if track.type == vlc.TrackType.video:
                    v = track.u.video.contents
                    orient = getattr(v.orientation, "value", v.orientation) or 0
                    shape = is_portrait(v.width, v.height, int(orient))
                    break
            out.append(shape)
        except Exception:
            out.append(None)
        finally:
            media.release()
    return out
