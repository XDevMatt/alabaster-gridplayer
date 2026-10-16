"""Whether a file is portrait or landscape, as VLC reads it, in a process
of its own (as FileLengths does) and remembered per file."""

import logging
import threading
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path

_log = logging.getLogger(__name__)

PARSE_TIMEOUT_MS = 3000

# (path, mtime_ns, size) -> True portrait, False landscape, None unknown
_cache: dict[tuple, bool | None] = {}
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
    if key in _cache:
        return _cache[key]
    shape = _probe(path)
    _cache[key] = shape
    return shape


def _probe(path: Path) -> bool | None:
    global _pool
    with _lock:
        if _pool is None:
            _pool = ProcessPoolExecutor(max_workers=1, mp_context=get_context("spawn"))
        pool = _pool
    try:
        return pool.submit(shapes_in_process, [str(path)]).result()[0]
    except Exception as e:
        _log.warning(f"File shape not read: {e}")
        with _lock:
            _pool = None
        pool.shutdown(wait=False, cancel_futures=True)
        return None


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
