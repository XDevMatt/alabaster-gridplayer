"""Separate audio, option B: a progressive video file whose sound is a file
of its own is handed to VLC with the sound as an input slave, both fetched
by VLC with the video's headers. Only for what VLC 3.0.24 was measured to
play in sync and seek in: a whole (not fragmented) MP4 or M4A (see
tests/real_app/test_separate_media_vlc.py)."""

import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from gridplayer.models.audio_selection import AudioLanguage
from gridplayer.models.stream import STREAM_QUALITY_AUTO
from gridplayer.models.video import Video
from gridplayer.settings import Settings
from gridplayer.utils.url_resolve.resolver_yt_dlp import YoutubeDLResolver
from gridplayer.vlc_player import vlc
from gridplayer.vlc_player.player_base import SLAVE_PRIORITY, VlcPlayerBase
from gridplayer.widgets.video_block_stream import StreamControl

PAGE = "http://host/watch"


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
def probe(mocker):
    """The one look at a file that says whether the site fragments them."""

    return mocker.patch(
        "gridplayer.utils.url_resolve.resolver_yt_dlp.is_fragmented_stream",
        return_value=False,
    )


@pytest.fixture(autouse=True)
def _timers(mocker):
    mocker.patch(
        "gridplayer.widgets.video_block_stream.QTimer",
        side_effect=lambda *args, **kwargs: Mock(),
    )


def _video(height=720, ext="mp4", **extra):
    return {
        "format_id": f"v{height}",
        "protocol": "https",
        "url": f"http://cdn/v{height}.{ext}",
        "ext": ext,
        "vcodec": "avc1.64001f",
        "acodec": "none",
        "height": height,
        "width": height * 16 // 9,
        "resolution": f"{height * 16 // 9}x{height}",
        "video_ext": ext,
        "tbr": height * 2.0,
        **extra,
    }


def _audio(language=None, ext="m4a", **extra):
    return {
        "format_id": f"a-{language}",
        "protocol": "https",
        "url": f"http://cdn/a-{language}.{ext}",
        "ext": ext,
        "vcodec": "none",
        "acodec": "mp4a.40.2",
        "language": language,
        "resolution": "audio only",
        "video_ext": "none",
        "abr": 128,
        **extra,
    }


def _resolver(formats):
    resolver = YoutubeDLResolver(PAGE)
    resolver.__dict__["_video_info"] = {
        "extractor": "generic",
        "title": "t",
        "is_live": False,
        "duration": 60,
        "formats": formats,
    }
    return resolver


def _rungs(formats):
    return list(_resolver(formats).streams.video_streams.values())


class TestTheResolver:
    def test_a_progressive_mp4_gets_its_m4a_as_a_slave(self):
        (stream,) = _rungs([_audio(), _video()])

        assert stream.is_audio_slaved is True
        assert stream.protocol == "http"
        assert stream.url == "http://cdn/v720.mp4"
        assert [t.url for _, t in stream.audio_tracks.items()] == [
            "http://cdn/a-None.m4a"
        ]

    def test_not_merged_through_the_callbacks(self):
        (stream,) = _rungs([_audio(), _video()])

        assert stream.protocol != "callback"

    def test_two_plain_files_are_not_demuxed_adaptively(self):
        """Each is a file VLC seeks in as a file."""

        (stream,) = _rungs([_audio(), _video()])

        assert stream.is_adaptive is False

    @pytest.mark.parametrize(
        ("video", "audio"),
        [
            # WebM beside WebM lost its sound or stalled on a seek
            (_video(ext="webm", vcodec="vp9"), _audio(ext="webm", acodec="opus")),
            # a fragmented MP4, as DASH serves it, does not seek at all
            (_video(container="mp4_dash"), _audio(container="m4a_dash")),
        ],
    )
    def test_what_vlc_could_not_seek_in_is_not_slaved(self, video, audio):
        for stream in _rungs([audio, video]):
            assert not stream.is_audio_slaved

    def test_a_site_that_fragments_its_files_is_not_slaved(self, probe):
        probe.return_value = True

        for stream in _rungs([_audio(), _video()]):
            assert not stream.is_audio_slaved

    def test_one_that_could_not_be_probed_is_not_slaved(self, probe):
        """It may be fragmented, and would not seek."""

        probe.side_effect = OSError("reset")

        for stream in _rungs([_audio(), _video()]):
            assert not stream.is_audio_slaved

    @pytest.mark.parametrize(
        "extra", [{"http_headers": {"Cookie": "sid=1"}}, {"impersonate": True}]
    )
    def test_one_vlc_cannot_fetch_itself_is_not_slaved(self, extra):
        for stream in _rungs([_audio(**extra), _video(**extra)]):
            assert not stream.is_audio_slaved

    def test_every_language_is_a_file_to_pick_from(self):
        (stream,) = _rungs([_audio("en"), _audio("de"), _video()])

        assert set(stream.audio_tracks.languages) == {"en", "de"}


def _block(mocker, streams, selection=None):
    block = mocker.Mock()
    block._log = logging.getLogger("test")
    block.streams = streams
    block.video_params = Video(uri=PAGE)
    block.video_params.audio_languages = ""
    if selection is not None:
        block.video_params.audio_selection = selection
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
    def test_vlc_gets_the_video_and_its_sound_as_a_slave(self, mocker):
        headers = {"User-Agent": "UA/1", "Referer": "http://host/"}
        streams = _resolver(
            [_audio(http_headers=headers), _video(http_headers=headers)]
        ).streams
        block = _block(mocker, streams)

        block.stream.load_quality(next(iter(streams)))

        media_input = _loaded(block)
        assert media_input.uri == "http://cdn/v720.mp4"
        assert media_input.stream_audio_slave == "http://cdn/a-None.m4a"
        assert media_input.callback_spec is None
        assert media_input.adaptive_max_height is None
        # the slave is fetched with these too (measured: VLC sends them)
        assert media_input.http_headers["User-Agent"] == "UA/1"
        assert media_input.http_headers["Referer"] == "http://host/"

    def test_the_sound_is_in_the_language_asked_for(self, mocker):
        streams = _resolver([_audio("en"), _audio("de"), _video()]).streams
        block = _block(mocker, streams, selection=AudioLanguage(tag="de"))

        block.stream.load_quality(next(iter(streams)))

        assert _loaded(block).stream_audio_slave == "http://cdn/a-de.m4a"


class TestThePlayer:
    def _player(self, uri):
        player = SimpleNamespace(
            media_input=SimpleNamespace(stream_audio_slave=uri),
            _media_input_vlc=Mock(),
            _log=logging.getLogger("test"),
        )
        return player

    def test_the_sound_file_goes_on_as_an_audio_slave(self):
        player = self._player("http://cdn/a.m4a")

        VlcPlayerBase._attach_stream_audio_slave(player)

        player._media_input_vlc.slaves_add.assert_called_once_with(
            vlc.MediaSlaveType.audio, SLAVE_PRIORITY, "http://cdn/a.m4a"
        )

    @pytest.mark.parametrize("uri", [None, "", "file:///etc/passwd", "smb://x/a"])
    def test_only_an_http_one(self, uri):
        player = self._player(uri)

        VlcPlayerBase._attach_stream_audio_slave(player)

        player._media_input_vlc.slaves_add.assert_not_called()
