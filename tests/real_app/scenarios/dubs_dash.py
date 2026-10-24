"""The dubbed stream as a DASH MPD, an audio adaptation set per language:
handed to VLC whole, as the HLS one is (option A)."""

from tests.real_app.scenarios._dubbing import SETTINGS, dubbed  # noqa: F401


def scenario(d):
    dubbed(d, "dash/manifest.mpd", "MPD")
