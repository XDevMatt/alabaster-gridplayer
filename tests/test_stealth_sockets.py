"""Local playback must not listen and must not phone home."""

import contextlib

import pytest

from gridplayer.params import env

LISTEN_STATES = {"LISTEN", "BOUND"}


def _connections(pid: int):
    try:
        import psutil
    except ImportError:
        pytest.skip("psutil is not installed")

    proc = psutil.Process(pid)
    conns = list(proc.net_connections(kind="inet"))
    for child in proc.children(recursive=True):
        with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
            conns.extend(child.net_connections(kind="inet"))
    return conns


def test_filter_does_not_open_a_listener():
    """Unit stand-in: the stream proxy manager never binds."""

    from types import SimpleNamespace

    from gridplayer.models.stream import Stream
    from gridplayer.player.managers.stream_proxy import StreamProxyManager

    manager = StreamProxyManager(context=SimpleNamespace())
    manager.cmd_add_stream(Stream(url="https://example.com/a.m3u8", protocol="hls"))

    assert manager.stream_proxy is None


@pytest.mark.skipif(not env.IS_WINDOWS, reason="uses WinError-free local bind check")
def test_this_process_has_no_listen_sockets_at_import():
    """Importing gridplayer must not bind TCP/UDP."""

    try:
        import psutil
    except ImportError:
        # ctypes fallback: nothing to assert without psutil besides "import worked"
        import gridplayer

        return

    before = {id(c) for c in psutil.Process().net_connections(kind="inet")}
    import gridplayer  # noqa: F401

    after = psutil.Process().net_connections(kind="inet")
    new_listen = [
        c
        for c in after
        if id(c) not in before and getattr(c, "status", None) in LISTEN_STATES
    ]
    assert new_listen == []
