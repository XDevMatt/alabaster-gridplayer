"""Separate audio, option A: a silent video and its audio renditions that
share an HLS master playlist (or a DASH MPD) are handed to VLC as that
manifest, whole. VLC pairs them itself: no merge through the callbacks, no
listener. The languages are VLC's own tracks, switched without a reload, and
the rung picked is the most its adaptive demuxer may show."""

import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from gridplayer.models.audio_selection import AudioLanguage, AudioPreferred
from gridplayer.models.stream import STREAM_QUALITY_AUTO
from gridplayer.models.video import Video
from gridplayer.settings import Settings
from gridplayer.utils.url_resolve.resolver_yt_dlp import YoutubeDLResolver
from gridplayer.vlc_player.player_base import _adaptive_options
from gridplayer.widgets.video_block_stream import StreamControl

MASTER = "http://host/dubs/master.m3u8"


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path):
    settings = Settings()
    real = settings.settings
    settings.settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)
    yield
    settings.settings = real


@pytest.fixture(autouse=True)
def _no_network(mocker):
    mocker.patch(
        "gridplayer.utils.url_resolve.resolver_yt_dlp.is_fragmented_stream",
        return_value=False,
    )


@pytest.fixture(autouse=True)
def _timers(mocker):
    mocker.patch(
        "gridplayer.widgets.video_block_stream.QTimer",
        side_effect=lambda *args, **kwargs: Mock(),
    )


# what yt-dlp 2026 returns for the real_app dubs master playlist, as read
# off it (tests/real_app/media.py)
def _rendition(language, name, manifest_url=MASTER, **extra):
    return {
        "format_id": f"group_aud-{name}",
        "protocol": "m3u8_native",
        "url": f"http://host/dubs/v{language}/index.m3u8",
        "manifest_url": manifest_url,
        "vcodec": "none",
        "acodec": None,
        "language": language,
        "ext": "mp4",
        **extra,
    }


def _variant(format_id, height, manifest_url=MASTER, **extra):
    return {
        "format_id": format_id,
        "protocol": "m3u8_native",
        "url": f"http://host/dubs/v{height}/index.m3u8",
        "manifest_url": manifest_url,
        "vcodec": "avc1.42c01e",
        "acodec": "none",
        "height": height,
        "width": height * 16 // 9,
        "resolution": f"{height * 16 // 9}x{height}",
        "video_ext": "mp4",
        "ext": "mp4",
        "tbr": height * 2.4,
        **extra,
    }


def _formats(**variant_extra):
    return [
        _rendition("es", "audio_3"),
        _rendition("en", "audio_2"),
        _variant("343", 180, **variant_extra),
        _variant("865", 360, **variant_extra),
    ]


def _resolver(formats):
    resolver = YoutubeDLResolver(MASTER)
    resolver.__dict__["_video_info"] = {
        "extractor": "generic",
        "title": "master",
        "is_live": False,
        "formats": formats,
    }
    return resolver


def _video_rungs(resolver):
    return dict(resolver.streams.video_streams.items())


# ---------------------------------------------------------------------------
# the resolver


class TestTheResolver:
    def test_every_rung_is_the_master_playlist_handed_over_whole(self):
        rungs = _video_rungs(_resolver(_formats()))

        assert len(rungs) == 2
        for stream in rungs.values():
            assert stream.url == MASTER
            assert stream.protocol == "hls"
            assert stream.is_whole_manifest is True

    def test_not_merged_through_the_callbacks(self):
        """What the fork did before: a yt-dlp merge to "-" that never
        reached VLC (docs/merges/fixes-20261023.md, section 2a)."""

        for stream in _video_rungs(_resolver(_formats())).values():
            assert stream.protocol != "callback"
            assert stream.format_id is not None

    def test_each_rung_is_the_most_vlc_may_pick(self):
        heights = sorted(
            stream.max_height for stream in _video_rungs(_resolver(_formats())).values()
        )

        assert heights == [180, 360]

    def test_the_languages_are_still_offered(self):
        stream = next(iter(_video_rungs(_resolver(_formats())).values()))

        assert set(stream.audio_tracks.languages) == {"en", "es"}

    def test_audio_from_another_manifest_is_not_handed_over_this_way(self):
        formats = [
            _rendition("es", "audio_3", manifest_url="http://other/master.m3u8"),
            _rendition("en", "audio_2"),
            _variant("343", 180),
        ]

        for stream in _video_rungs(_resolver(formats)).values():
            assert not stream.is_whole_manifest

    def test_a_header_vlc_cannot_send_keeps_it_off_vlc(self):
        """VLC would fetch the manifest without it."""

        formats = _formats(http_headers={"Cookie": "sid=1"})

        for stream in _video_rungs(_resolver(formats)).values():
            assert not stream.is_whole_manifest
            assert stream.protocol == "callback"

    def test_one_only_a_browser_can_fetch_keeps_it_off_vlc(self):
        formats = _formats(impersonate=True)

        for stream in _video_rungs(_resolver(formats)).values():
            assert not stream.is_whole_manifest

    @pytest.mark.parametrize(
        "manifest", ["file:///etc/master.m3u8", "ftp://host/master.m3u8", ""]
    )
    def test_only_an_http_manifest_is_handed_over(self, manifest):
        formats = [
            _rendition("es", "audio_3", manifest_url=manifest),
            _rendition("en", "audio_2", manifest_url=manifest),
            _variant("343", 180, manifest_url=manifest),
        ]

        for stream in _video_rungs(_resolver(formats)).values():
            assert not stream.is_whole_manifest

    def test_a_dash_mpd_is_handed_over_as_it_is(self):
        mpd = "http://host/dubs/manifest.mpd"
        dash = {
            "protocol": "http_dash_segments",
            "url": mpd,
            "manifest_url": mpd,
            "container": "mp4_dash",
            "fragment_base_url": "http://host/dash/",
            "fragments": [{"path": "init.m4s"}, {"path": "0.m4s", "duration": 4.0}],
        }
        formats = [
            {**_rendition("es", "a-es"), **dash, "acodec": "mp4a.40.2"},
            {**_rendition("en", "a-en"), **dash, "acodec": "mp4a.40.2"},
            {**_variant("v720", 720), **dash},
        ]

        (stream,) = _video_rungs(_resolver(formats)).values()

        assert stream.url == mpd
        assert stream.protocol == "direct"
        assert stream.is_whole_manifest is True
        assert stream.max_height == 720
        assert not stream.fragments

    def test_dash_rungs_of_the_one_mpd_stay_rungs(self):
        """Not collapsed into one "Adaptive": each is VLC's most to pick."""

        mpd = "http://host/dubs/manifest.mpd"
        dash = {"protocol": "http_dash_segments", "url": mpd, "manifest_url": mpd}
        formats = [
            {**_rendition("es", "a-es"), **dash, "acodec": "mp4a.40.2"},
            {**_rendition("en", "a-en"), **dash, "acodec": "mp4a.40.2"},
            {**_variant("v180", 180), **dash},
            {**_variant("v360", 360), **dash},
        ]

        heights = sorted(
            s.max_height for s in _video_rungs(_resolver(formats)).values()
        )

        assert heights == [180, 360]


# ---------------------------------------------------------------------------
# what VLC is told


class TestWhatVlcIsTold:
    def test_the_rung_is_its_adaptive_maxheight(self):
        assert _adaptive_options(180) == [":adaptive-maxheight=180"]

    @pytest.mark.parametrize("height", [None, 0, -1])
    def test_none_leaves_it_every_rung(self, height):
        assert _adaptive_options(height) == []


def _block(mocker, streams, selection=None):
    block = mocker.Mock()
    block._log = logging.getLogger("test")
    block.streams = streams
    block.video_params = Video(uri=MASTER)
    block.video_params.audio_languages = ""
    block.video_params.audio_selection = selection or AudioPreferred()
    block.video_params.stream_quality = STREAM_QUALITY_AUTO
    block._item_headers = {}
    block.is_live = False
    block.size_tuple = (640, 360)
    block.list_aspect_ratio = ""
    block.list_crop_ratio = ""
    block.stream = StreamControl(block)
    return block


def _loaded(block):
    (media_input,), _ = block.load_video.emit.call_args
    return media_input


class TestTheCell:
    def test_vlc_gets_the_master_and_the_rung_as_its_most(self, mocker):
        block = _block(mocker, _resolver(_formats()).streams)
        rung = next(name for name, s in block.streams.items() if s.max_height == 180)

        block.stream.load_quality(rung)

        media_input = _loaded(block)
        assert media_input.uri == MASTER
        assert media_input.adaptive_max_height == 180
        assert media_input.callback_spec is None

    def test_another_language_is_vlcs_own_track_with_no_reload(self, mocker):
        block = _block(mocker, _resolver(_formats()).streams)
        block.stream.load_quality(next(iter(block.streams)))
        block.reset.reset_mock()
        block.load_video.emit.reset_mock()

        block.stream.set_audio_language("es")

        assert block.video_params.audio_selection == AudioLanguage(tag="es")
        block.reset.assert_not_called()
        block.load_video.emit.assert_not_called()
        block.audio.apply_wanted_track.assert_called()

    def test_the_language_said_playing_is_the_track_vlc_plays(self, mocker):
        block = _block(mocker, _resolver(_formats()).streams)
        block.stream.load_quality(next(iter(block.streams)))
        block.audio.tracks = {
            0: SimpleNamespace(language="es"),
            1: SimpleNamespace(language="en"),
        }

        block.audio.track_playing = 0
        assert block.stream.audio_language_playing == "es"

        block.audio.track_playing = 1
        assert block.stream.audio_language_playing == "en"

    def test_a_language_vlc_does_not_name_falls_back_to_the_one_loaded(self, mocker):
        block = _block(mocker, _resolver(_formats()).streams)
        block.stream.load_quality(next(iter(block.streams)))
        block.audio.tracks = {0: SimpleNamespace(language=None)}
        block.audio.track_playing = 0

        assert block.stream.audio_language_playing in {"en", "es"}
