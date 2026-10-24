"""A stream dubbed into two languages: switching between them, and keeping
the one chosen through a change of size.

VLC is handed the HLS master playlist whole (option A in
docs/merges/fixes-20261023.md): the languages are its own tracks, switched
without a reload, and the rung picked is the most it may show."""

from tests.real_app.scenarios._dubbing import SETTINGS, dubbed  # noqa: F401


def scenario(d):
    dubbed(d, "master.m3u8", "master playlist")
