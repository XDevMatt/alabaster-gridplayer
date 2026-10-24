"""A stream VLC cannot fetch by itself, fed to it by yt-dlp through the
media callbacks (Alabaster has no local proxy), and switched to another
size the same way.

Fed as a pipe, VLC knows neither its length nor how to seek in it, so the
app takes it for live and its time stays 0: what says it plays is VLC
taking more of it as it goes.
"""


def scenario(d):
    from gridplayer.utils import ytdlp_byte_source
    from gridplayer.utils.url_resolve import resolver_yt_dlp

    # as if the site asked for a header VLC cannot send: only yt-dlp may
    # fetch it, posing as what the site wants
    resolver_yt_dlp._headers_need_callback = lambda headers: True

    fed = []
    real_read = ytdlp_byte_source.YtdlpByteSource.read

    def read(self, n):
        data = real_read(self, n)
        if data:
            fed.append(len(data))
        return data

    ytdlp_byte_source.YtdlpByteSource.read = read

    d.open(f"{d.serve(d.media.hls)}/master.m3u8")
    cell = d.wait_for_cell("master.m3u8")

    d.wait_until(
        lambda: cell.is_playable and sum(fed) > 0,
        "it plays through the callbacks",
        timeout=30,
    )
    d.check("taken for live", cell.is_live)
    d.shot("callback_playing")
    d.check("not in error", not cell.is_error, cell.status.last_error)

    before = sum(fed)
    d.choose(cell, "menu_generator_stream_quality", "180p")
    d.wait_until(
        lambda: (
            (cell.stream.quality_playing or "").startswith("180p")
            and cell.is_playable
            and sum(fed) > before
        ),
        "180p plays through the callbacks",
        timeout=30,
    )
    d.check("fed again after the switch", sum(fed) > before, sum(fed) - before)

    d.note("end", cell)
