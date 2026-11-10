"""The proxy's DASH relay answers only for what it registered.

Alabaster hands live DASH to VLC as the manifest and starts no proxy
listener, so the tests that fetched a manifest and its segments through
upstream's loopback relay are gone;
what is left asks the relay class itself.
"""

import pytest
import requests

from gridplayer.utils.stream_proxy.server import ProxyRequestHandler, StreamProxyServer


@pytest.fixture
def proxy(serving):
    return serving(StreamProxyServer(("127.0.0.1", 0), ProxyRequestHandler))


class TestTheSegmentsUnderIt:
    def test_a_base_nobody_handed_out_is_not_served(self, local_login, proxy):
        """The relay answers for what it registered, not for any URL asked of it."""

        response = requests.get(f"{proxy.base_url}/dash/made-up/V300/0.m4s", timeout=5)

        assert response.status_code == 404

    def test_a_base_nobody_handed_out_is_said_to_be_missing(self, proxy):
        """404 either way, but only one of them says what was not found.

        Falling through to the query the rest of the proxy uses would
        report a session that was never asked for.
        """

        with pytest.raises(LookupError, match="made-up"):
            proxy.dash_query("/dash/made-up/V300/0.m4s")

    def test_a_request_that_is_not_a_relayed_segment_is_left_alone(self, proxy):
        assert proxy.dash_query("/?url=http%3A%2F%2Fhost%2Fv.mp4") is None
