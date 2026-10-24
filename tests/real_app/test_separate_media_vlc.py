"""What options A and B rely on VLC 3 for, measured on the VLC the app
ships, over plain http from a server that lives only in this test (the app
itself gets no listener).

- A: a manifest handed over whole, the rung picked as :adaptive-maxheight.
- B: a progressive video with its sound file as an input slave: plays, in
  sync, and seeks back and forth. A fragmented MP4 does not seek at all,
  which is why B leaves those alone (a change here means looking again).

Sync is read off the video and audio callbacks: the test video flashes
white and the test audio beeps at every whole second, and the offset is
when VLC shows the one minus when it plays the other.
"""

import ctypes
import functools
import shutil
import statistics
import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest

from gridplayer.vlc_player import vlc
from tests.real_app import media

pytestmark = [
    pytest.mark.real_app,
    pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg"),
]

W, H, RATE = 32, 18, 48000
LOUD = 3000


class _Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        """Quiet"""

    def do_GET(self):
        self.server.seen.append(
            (self.path, self.headers.get("User-Agent"), self.headers.get("Referer"))
        )
        try:
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            pass


@pytest.fixture(scope="module")
def files(tmp_path_factory):
    where = tmp_path_factory.mktemp("separate")
    flash = (
        "drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable='lt(mod(t\\,1)\\,0.04)'"
    )
    beep = (
        "aevalsrc='if(lt(mod(t\\,1)\\,0.04)\\,0.8*sin(2*PI*1000*t)\\,0)':s=48000:d=40"
    )

    def ff(*args):
        subprocess.run(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *args],
            cwd=where,
            check=True,
        )

    ff("-f", "lavfi", "-i", "color=c=black:s=320x180:r=25:d=40", "-vf", flash,
       "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-g", "25",
       "-movflags", "+faststart", "-an", "video.mp4")  # fmt: skip
    ff("-f", "lavfi", "-i", beep, "-c:a", "aac", "-movflags", "+faststart", "audio.m4a")
    ff("-i", "video.mp4", "-c", "copy", "-movflags", "+dash+global_sidx", "frag.mp4")
    return where


@pytest.fixture(scope="module")
def serve():
    servers = []

    def _serve(directory):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), functools.partial(_Handler, directory=str(directory))
        )
        server.seen = []
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        return server, f"http://127.0.0.1:{server.server_address[1]}"

    yield _serve

    for server in servers:
        server.shutdown()


@pytest.fixture(scope="module")
def instance():
    return vlc.Instance(["--quiet", "--no-xlib", "--avcodec-hw=none"])


class _Probe:
    """When VLC shows each flash and plays each beep, on VLC's own clock
    (CLOCK_MONOTONIC, the one time.monotonic reads)."""

    def __init__(self, player):
        self.buf = (ctypes.c_uint8 * (W * H * 4))()
        self.flashes, self.beeps = [], []
        self._white = self._loud = False
        cb = vlc.CallbackDecorators
        self._cbs = (
            cb.VideoLockCb(self._lock),
            cb.VideoUnlockCb(lambda *a: None),
            cb.VideoDisplayCb(self._display),
            cb.AudioPlayCb(self._play),
            cb.AudioPauseCb(lambda *a: None),
            cb.AudioResumeCb(lambda *a: None),
            cb.AudioFlushCb(self._flush),
            cb.AudioDrainCb(lambda *a: None),
        )
        player.video_set_callbacks(*self._cbs[:3], None)
        player.video_set_format("RV32", W, H, W * 4)
        player.audio_set_callbacks(*self._cbs[3:], None)
        player.audio_set_format("S16N", RATE, 1)

    def _lock(self, opaque, planes):
        planes[0] = ctypes.cast(self.buf, ctypes.c_void_p)

    def _display(self, opaque, picture):
        white = sum(self.buf[0::4][: W * H]) / (W * H) > 128
        if white and not self._white:
            self.flashes.append(time.monotonic())
        self._white = white

    def _flush(self, opaque, pts):
        self._loud = False

    def _play(self, opaque, samples, count, pts):
        data = ctypes.cast(samples, ctypes.POINTER(ctypes.c_int16 * count)).contents
        for i in range(0, count, 8):
            loud = abs(data[i]) > LOUD
            if loud and not self._loud:
                self.beeps.append(pts / 1e6 + i / RATE)
            self._loud = loud or (self._loud and i % 480 != 0)
        if not any(abs(data[j]) > LOUD for j in range(max(0, count - 64), count)):
            self._loud = False

    def offsets_ms(self, since, until):
        found = []
        for flash in (t for t in self.flashes if since <= t <= until):
            beep = min(self.beeps, key=lambda b: abs(b - flash), default=None)
            if beep is not None and abs(beep - flash) < 0.45:
                found.append((flash - beep) * 1000)
        return found


def _play(instance, url, slave=None, options=()):
    player = instance.media_player_new()
    item = instance.media_new(url, *options)
    if slave:
        item.slaves_add(vlc.MediaSlaveType.audio, 4, slave)
    player.set_media(item)
    probe = _Probe(player)
    player.play()
    return player, probe


def _window(probe, seconds):
    start = time.monotonic()
    time.sleep(seconds)
    return probe.offsets_ms(start, time.monotonic())


class TestOptionB:
    def test_a_progressive_video_with_its_sound_as_a_slave(
        self, files, serve, instance
    ):
        server, base = serve(files)
        player, probe = _play(
            instance,
            f"{base}/video.mp4",
            slave=f"{base}/audio.m4a",
            options=(":http-user-agent=GP/1", ":http-referrer=http://page/"),
        )

        try:
            first = _window(probe, 6)
            assert len(first) >= 4, "plays, picture and sound both"
            reference = statistics.median(first)
            assert abs(reference) < 45

            # drift: the same offset ten seconds on
            later = _window(probe, 10)
            assert len(later) >= 8
            assert abs(statistics.median(later) - reference) < 5

            for target in (25_000, 5_000, 30_000, 12_000, 2_000):
                player.set_time(target)
                time.sleep(1.5)
                after = _window(probe, 3)

                assert abs(player.get_time() - (target + 4_500)) < 1_500, target
                assert len(after) >= 2, f"picture and sound after a seek to {target}"
                assert abs(statistics.median(after) - reference) < 5, target
        finally:
            player.stop()

        fetched = {(path, ua, ref) for path, ua, ref in server.seen}
        assert ("/audio.m4a", "GP/1", "http://page/") in fetched

    def test_vlc_does_not_seek_in_a_fragmented_mp4(self, files, serve, instance):
        """Why B leaves DASH and YouTube's separate files alone: should VLC
        learn to, this fails, and B can take them on."""

        _, base = serve(files)
        player, _probe = _play(instance, f"{base}/frag.mp4")

        try:
            time.sleep(2)
            player.set_time(30_000)
            time.sleep(2)

            assert player.get_time() < 10_000
        finally:
            player.stop()


class TestOptionA:
    @pytest.fixture(scope="class")
    def master(self, serve):
        _, base = serve(media.ensure().dubs)
        return f"{base}/master.m3u8"

    def _heights_and_languages(self, instance, url, options=()):
        player = instance.media_player_new()
        item = instance.media_new(url, *options)
        player.set_media(item)
        player.play()
        try:
            time.sleep(4)
            # a generator: read once
            tracks = list(item.tracks_get() or [])
            heights = {
                t.u.video.contents.height
                for t in tracks
                if t.type == vlc.TrackType.video
            }
            languages = {
                t.language.decode()
                for t in tracks
                if t.type == vlc.TrackType.audio and t.language
            }
            return heights, languages, player.get_time()
        finally:
            player.stop()

    def test_the_master_playlist_carries_every_language(self, instance, master):
        _heights, languages, played = self._heights_and_languages(instance, master)

        assert {"en", "es"} <= languages
        assert played > 1_000

    def test_the_rung_is_the_most_vlc_may_pick(self, instance, master):
        heights, _languages, _ = self._heights_and_languages(
            instance, master, (":adaptive-maxheight=180",)
        )

        assert heights == {180}
