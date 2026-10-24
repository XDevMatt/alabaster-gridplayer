"""Pull media bytes from the bundled yt-dlp module into libVLC callbacks.

No TCP or UDP listener: a queue in this process, read from VLC's threads.
Used when VLC cannot fetch the URL itself (TLS impersonation, extra
headers, muxing separate audio and video).
"""

from __future__ import annotations

import contextlib
import io
import logging
import queue
import sys
import threading
from typing import TYPE_CHECKING

from gridplayer.utils.cookies import ytdl_cookies
from gridplayer.utils.js_runtime import ytdl_js_runtimes
from gridplayer.utils.network import ytdl_network_opts
from gridplayer.utils.percent_re import untangle_percent_re

if TYPE_CHECKING:
    from gridplayer.vlc_player.static import MediaCallbackSpec

_log = logging.getLogger(__name__)

CHUNK_QUEUE_SIZE = 8
READ_WAIT_S = 0.25


class YtdlpByteSource:
    def __init__(self, spec: MediaCallbackSpec):
        self.spec = spec
        self._queue: queue.Queue[bytes | None] = queue.Queue(maxsize=CHUNK_QUEUE_SIZE)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._error: BaseException | None = None
        self._leftover = b""

    def start(self) -> None:
        if self._thread is not None:
            return

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._download, name="ytdlp-byte-source", daemon=True
        )
        self._thread.start()

    def read(self, n: int) -> bytes | None:
        """Up to n bytes, b'' at EOF, None on a hard error or stop."""

        if n <= 0:
            return b""

        if self._error is not None:
            return None

        while len(self._leftover) < n:
            if self._stop.is_set():
                return None

            try:
                chunk = self._queue.get(timeout=READ_WAIT_S)
            except queue.Empty:
                if self._error is not None:
                    return None
                if self._thread is None or not self._thread.is_alive():
                    break
                continue

            if chunk is None:
                break

            self._leftover += chunk

        if not self._leftover and self._error is not None:
            return None

        out = self._leftover[:n]
        self._leftover = self._leftover[n:]
        return out

    def close(self) -> None:
        self._stop.set()
        _drain_queue(self._queue)
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _download(self) -> None:
        writer = _QueueWriter(self._queue, self._stop)

        try:
            # inside the try: whatever goes wrong before the download starts
            # has to reach read() as an error too, not as an empty stream
            untangle_percent_re()

            from yt_dlp import YoutubeDL

            with (
                _stdout_to(writer),
                ytdl_cookies() as cookie_opts,
                YoutubeDL({**self._ydl_opts(), **cookie_opts}) as ydl,
            ):
                ydl.download([self.spec.page_url])
        except Exception as e:
            if not self._stop.is_set():
                _log.debug("yt-dlp callback download failed: %s", e)
                self._error = e
        finally:
            writer.close()

    def _ydl_opts(self) -> dict:
        ydl_opts = {
            "outtmpl": "-",
            "noprogress": True,
            "quiet": True,
            "no_warnings": True,
            "logtostderr": True,
            "merge_output_format": "mpegts",
            "hls_use_mpegts": True,
            "js_runtimes": ytdl_js_runtimes(),
            **ytdl_network_opts(),
        }

        if self.spec.format_id:
            ydl_opts["format"] = self.spec.format_id

        if self.spec.impersonate:
            ydl_opts["impersonate"] = self.spec.impersonate

        if self.spec.headers:
            ydl_opts["http_headers"] = {
                **ydl_opts.get("http_headers", {}),
                **self.spec.headers,
            }

        return ydl_opts


class _QueueWriter(io.RawIOBase):
    def __init__(self, chunks: queue.Queue, stop: threading.Event):
        super().__init__()
        self._chunks = chunks
        self._stop = stop
        self._closed = False

    def writable(self) -> bool:
        return True

    def write(self, b) -> int:
        if self._closed or self._stop.is_set():
            raise OSError("callback source closed")

        data = bytes(b)
        if not data:
            return 0

        while not self._stop.is_set():
            with contextlib.suppress(queue.Full):
                self._chunks.put(data, timeout=READ_WAIT_S)
                return len(data)

        raise OSError("callback source stopped")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._chunks.put_nowait(None)
        except queue.Full:
            _drain_queue(self._chunks)
            with contextlib.suppress(queue.Full):
                self._chunks.put_nowait(None)


class _ThreadStdout(io.TextIOBase):
    """sys.stdout for the whole process, with a byte source's thread given
    its own.

    yt-dlp writes a download to "-" through ``sys.stdout.buffer``, read
    once as the download starts. Swapping sys.stdout itself for each
    download was process-wide: two cells on callbacks at once took each
    other's bytes, and the first to finish put the real stdout back under
    the other. Here every other thread still writes where it always did.
    """

    def __init__(self, fallback):
        super().__init__()
        self._fallback = fallback
        self._local = threading.local()

    def _target(self) -> _QueueWriter | None:
        return getattr(self._local, "target", None)

    @property
    def encoding(self):
        return getattr(self._fallback, "encoding", None) or "utf-8"

    @property
    def errors(self):
        return getattr(self._fallback, "errors", None) or "replace"

    @property
    def buffer(self):
        target = self._target()
        if target is not None:
            return target

        # a GUI build has no stdout at all
        fallback_buffer = getattr(self._fallback, "buffer", None)
        if fallback_buffer is None:
            raise AttributeError("buffer")
        return fallback_buffer

    def writable(self) -> bool:
        return True

    def write(self, s) -> int:
        target = self._target()
        if target is not None:
            data = s.encode("utf-8") if isinstance(s, str) else bytes(s)
            target.write(data)
            return len(s)

        if self._fallback is None:
            return len(s)
        return self._fallback.write(s)

    def flush(self) -> None:
        if self._target() is None and self._fallback is not None:
            self._fallback.flush()

    def isatty(self) -> bool:
        if self._target() is not None or self._fallback is None:
            return False
        return self._fallback.isatty()

    def fileno(self):
        # yt-dlp asks for it on Windows to set binary mode, and copes without
        if self._target() is not None or self._fallback is None:
            raise io.UnsupportedOperation("not a real stdout")
        return self._fallback.fileno()


_STDOUT_LOCK = threading.Lock()


@contextlib.contextmanager
def _stdout_to(writer: _QueueWriter):
    """What this thread writes to sys.stdout goes to writer, for a while."""

    with _STDOUT_LOCK:
        if not isinstance(sys.stdout, _ThreadStdout):
            sys.stdout = _ThreadStdout(sys.stdout)
        stdout = sys.stdout

    stdout._local.target = writer
    try:
        yield
    finally:
        stdout._local.target = None


def _drain_queue(chunks: queue.Queue) -> None:
    with contextlib.suppress(queue.Empty):
        while True:
            chunks.get_nowait()
