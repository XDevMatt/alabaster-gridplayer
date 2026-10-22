"""yt-dlp feeds VLC through a queue, with no listening socket."""

import pickle
from types import SimpleNamespace

from gridplayer.models.stream import Stream
from gridplayer.player.managers.stream_proxy import StreamProxyManager
from gridplayer.utils.ytdlp_byte_source import YtdlpByteSource, _QueueWriter
from gridplayer.vlc_player.static import MediaCallbackSpec


def test_callback_spec_survives_pickle():
    spec = MediaCallbackSpec(
        page_url="https://kick.com/x",
        format_id="hls-720",
        impersonate="chrome",
        headers={"User-Agent": "Mozilla"},
    )

    clone = pickle.loads(pickle.dumps(spec))

    assert clone.page_url == spec.page_url
    assert clone.format_id == spec.format_id
    assert clone.impersonate == spec.impersonate
    assert clone.headers == spec.headers


def test_queue_writer_delivers_bytes_then_eof():
    import queue
    import threading

    chunks = queue.Queue()
    stop = threading.Event()
    writer = _QueueWriter(chunks, stop)
    writer.write(b"abc")
    writer.write(b"def")
    writer.close()

    assert chunks.get_nowait() == b"abc"
    assert chunks.get_nowait() == b"def"
    assert chunks.get_nowait() is None


def test_byte_source_read_concatenates_chunks(monkeypatch):
    spec = MediaCallbackSpec(page_url="https://example.com/v")
    source = YtdlpByteSource(spec)
    source._queue.put(b"hello ")
    source._queue.put(b"world")
    source._queue.put(None)

    assert source.read(5) == b"hello"
    assert source.read(10) == b" world"
    assert source.read(10) == b""


def test_stream_proxy_manager_does_not_start_a_listener():
    manager = StreamProxyManager(context=SimpleNamespace())

    url = manager.cmd_add_stream(
        Stream(url="https://example.com/live.m3u8", protocol="hls")
    )

    assert url == "https://example.com/live.m3u8"
    assert manager.stream_proxy is None
