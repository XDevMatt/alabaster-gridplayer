"""A subtitle file dropped on a cell is shown with what the cell plays,
and does not open a new cell of its own."""

import gc

from gridplayer.player.managers.drag_n_drop import DragNDropManager


def scenario(d):
    d.open(d.media.feature)
    b = d.wait_for_cell("feature.mkv")
    d.wait_until(lambda: len(b.subtitles.tracks) >= 2, "own subtitles listed")
    before = len(b.subtitles.tracks)
    cells = len(d.ctx.video_blocks)

    srt = d.out / "dropped.srt"
    srt.write_text("1\n00:00:00,000 --> 00:01:00,000\nDropped\n", encoding="utf-8")

    dnd = next(o for o in gc.get_objects() if isinstance(o, DragNDropManager))
    dnd._finish_drop([str(srt)], None, None, b, None, False)

    d.wait_until(lambda: len(b.subtitles.tracks) > before, "dropped srt adds a track")
    d.check("no new cell", len(d.ctx.video_blocks) == cells, len(d.ctx.video_blocks))
    d.check(
        "dropped srt attached",
        srt.resolve() in b.video_params.external_subtitles,
        [str(p) for p in b.video_params.external_subtitles],
    )
