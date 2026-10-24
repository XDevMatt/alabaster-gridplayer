"""yt-dlp feeds VLC through a queue, with no listening socket."""

import contextlib
import functools
import pickle
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

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


# ---------------------------------------------------------------------------
# A real download through yt-dlp, from a server on this machine


@pytest.fixture
def served(tmp_path):
    """Two files of different bytes, served over http on 127.0.0.1."""

    files = {
        "one.mp4": bytes(range(256)) * 700,
        "two.mp4": bytes(reversed(range(256))) * 900,
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.RequestHandlerClass.log_message = lambda *args: None
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{server.server_port}", files

    server.shutdown()
    server.server_close()


@pytest.fixture
def no_network_settings(monkeypatch):
    from gridplayer.utils import ytdlp_byte_source as module

    monkeypatch.setattr(module, "ytdl_network_opts", dict)
    monkeypatch.setattr(module, "ytdl_js_runtimes", dict)
    monkeypatch.setattr(module, "ytdl_cookies", lambda: contextlib.nullcontext({}))


def _read_all(source, timeout=30):
    data = b""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        chunk = source.read(65536)
        if chunk is None:
            raise AssertionError(f"the source failed: {source._error!r}")
        if not chunk:
            return data
        data += chunk
    raise AssertionError("the source never ended")


def test_the_bytes_yt_dlp_downloads_reach_vlc(served, no_network_settings):
    base, files = served
    source = YtdlpByteSource(MediaCallbackSpec(page_url=f"{base}/one.mp4"))
    source.start()
    try:
        assert _read_all(source) == files["one.mp4"]
    finally:
        source.close()


def test_two_at_once_each_get_their_own(served, no_network_settings, capsys):
    """The download goes to sys.stdout as yt-dlp sees it; two cells on the
    callbacks at once must not get each other's bytes, and the rest of the
    app still prints where it did."""

    base, files = served
    sources = {
        name: YtdlpByteSource(MediaCallbackSpec(page_url=f"{base}/{name}"))
        for name in files
    }
    got = {}

    def drain(name):
        got[name] = _read_all(sources[name])

    for source in sources.values():
        source.start()
    readers = [threading.Thread(target=drain, args=(name,)) for name in files]
    for reader in readers:
        reader.start()
    print("still the app's own")
    for reader in readers:
        reader.join(timeout=60)
    for source in sources.values():
        source.close()

    assert got == files
    assert "still the app's own" in capsys.readouterr().out


def test_a_failure_before_the_download_is_an_error_not_an_empty_stream(
    no_network_settings, monkeypatch
):
    from gridplayer.utils import ytdlp_byte_source as module

    def broken():
        raise RuntimeError("no runtimes")

    monkeypatch.setattr(module, "ytdl_js_runtimes", broken)
    source = YtdlpByteSource(MediaCallbackSpec(page_url="http://127.0.0.1:9/x.mp4"))
    source.start()
    try:
        assert source.read(10) is None
        assert isinstance(source._error, RuntimeError)
    finally:
        source.close()
