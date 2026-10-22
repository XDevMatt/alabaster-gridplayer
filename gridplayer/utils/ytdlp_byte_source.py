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
        untangle_percent_re()

        from yt_dlp import YoutubeDL

        writer = _QueueWriter(self._queue, self._stop)
        stdout = _StdoutToBuffer(writer)
        old_stdout = sys.stdout

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

        try:
            sys.stdout = stdout
            with (
                ytdl_cookies() as cookie_opts,
                YoutubeDL({**ydl_opts, **cookie_opts}) as ydl,
            ):
                ydl.download([self.spec.page_url])
        except Exception as e:
            if not self._stop.is_set():
                _log.debug("yt-dlp callback download failed: %s", e)
                self._error = e
        finally:
            sys.stdout = old_stdout
            writer.close()


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


class _StdoutToBuffer(io.TextIOBase):
    """What yt-dlp writes to when outtmpl is '-'."""

    def __init__(self, buffer: _QueueWriter):
        super().__init__()
        self.buffer = buffer
        self.encoding = "utf-8"
        self.errors = "replace"
        self.name = "-"

    def fileno(self):
        raise io.UnsupportedOperation("not a real stdout")

    def write(self, s) -> int:
        if isinstance(s, str):
            data = s.encode("utf-8")
        else:
            data = bytes(s)
        return self.buffer.write(data)

    def flush(self) -> None:
        return None

    def isatty(self) -> bool:
        return False


def _drain_queue(chunks: queue.Queue) -> None:
    with contextlib.suppress(queue.Empty):
        while True:
            chunks.get_nowait()
