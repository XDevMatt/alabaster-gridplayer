"""A plain file, with no proxy configured, is handed straight to VLC.

Upstream relayed a link through its loopback stream proxy when the user
had set a proxy of their own; Alabaster starts no such listener, so the
tests that followed bytes through that relay are gone. The origin and the forwarding proxy stay
so the remaining test can say nothing went through a proxy.
"""

import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from gridplayer.utils.url_resolve.resolver_base import DirectResolver

BODY = bytes(range(256)) * 64

TIMEOUT_SEC = 5


class OriginHandler(BaseHTTPRequestHandler):
    """The host the file is actually on."""

    protocol_version = "HTTP/1.1"

    def do_GET(self):
        wanted = _wanted_range(self.headers.get("Range"))

        if wanted is None:
            self._send(HTTPStatus.OK, BODY)
            return

        start, end = wanted

        self._send(
            HTTPStatus.PARTIAL_CONTENT,
            BODY[start : end + 1],
            {"Content-Range": f"bytes {start}-{end}/{len(BODY)}"},
        )

    def _send(self, status, body, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")

        for name, value in (headers or {}).items():
            self.send_header(name, value)

        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Quiet, the test is not interested"""


class ForwardingHandler(BaseHTTPRequestHandler):
    """An HTTP proxy, which is to say a host given the whole URL.

    A request line carrying an absolute URL is the only thing that tells
    a proxy apart from an origin, so what it was given is recorded and
    is the whole of what this test is asking about.
    """

    protocol_version = "HTTP/1.1"

    def do_GET(self):
        self.server.seen.append(self.path)

        onward = urllib.request.Request(self.path)

        wanted = self.headers.get("Range")
        if wanted:
            onward.add_header("Range", wanted)

        with urllib.request.urlopen(onward, timeout=TIMEOUT_SEC) as answer:
            body = answer.read()
            status = answer.status
            content_range = answer.headers.get("Content-Range")

        self.send_response(status)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(len(body)))

        if content_range:
            self.send_header("Content-Range", content_range)

        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Quiet, the test is not interested"""


def _wanted_range(header):
    if not header:
        return None

    start, _, end = header.removeprefix("bytes=").partition("-")

    return int(start), int(end) if end else len(BODY) - 1


@pytest.fixture
def origin(serving):
    return serving(ThreadingHTTPServer(("127.0.0.1", 0), OriginHandler))


@pytest.fixture
def forwarder(serving):
    server = ThreadingHTTPServer(("127.0.0.1", 0), ForwardingHandler)
    server.seen = []

    return serving(server)


def _url_of(server):
    address, port = server.server_address

    return f"http://{address}:{port}"


def _video_url(origin):
    return f"{_url_of(origin)}/video.mp4"


class TestWithNothingConfigured:
    def test_the_link_is_handed_straight_to_vlc(self, origin, forwarder):
        """No proxy, no cookie: the relay would cost a hop and buy nothing."""

        stream = DirectResolver(_video_url(origin)).streams["generic"]

        assert stream.protocol == "direct"
        assert forwarder.seen == []
