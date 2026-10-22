from threading import Lock

from gridplayer.models.stream import Stream
from gridplayer.player.managers.base import ManagerBase


class StreamProxyManager(ManagerBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._stream_proxy_lock = Lock()
        self._stream_proxy = None

    @property
    def stream_proxy(self):
        """The localhost HTTP listener is no longer started."""

        return None

    @property
    def commands(self):
        return {
            "add_stream": self.cmd_add_stream,
            "stream_failure": self.cmd_stream_failure,
        }

    def cmd_add_stream(self, stream: Stream) -> str:
        """Return the media URL. A ThreadingHTTPServer is not started."""

        return stream.url

    def cmd_stream_failure(self, url: str):
        """What the stream behind a URL of the proxy's last could not be
        fetched for, None for nothing; never starting the proxy to say."""

        with self._stream_proxy_lock:
            proxy = self._stream_proxy

        if proxy is None:
            return None

        return proxy.server.failure_of(url)

    def cleanup(self):
        if self._stream_proxy is not None:
            self._stream_proxy.cleanup()
            self._stream_proxy = None
