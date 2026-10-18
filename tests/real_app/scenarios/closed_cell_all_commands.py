"""A command for all cells (Shift+. sets loop end) after one cell was
closed reaches only the cells still open: the closed one's parts are no
longer connected, so nothing reaches a deleted block."""


def scenario(d):
    one = d.media.shapes / "wide1.mp4"
    two = d.media.shapes / "wide2.mp4"

    d.open(one, two)
    a = d.wait_for_cell("wide1.mp4")
    b = d.wait_for_cell("wide2.mp4")

    a.close()
    d.wait_until(lambda: len(d.cells) == 1, "one cell left")
    d.pump(1.0)

    for name in ("Set Loop End [ALL]", "Set Loop Start [ALL]", "Loop Reset [ALL]"):
        d.act(b, name)
    d.pump(0.5)
    d.act(b, "Set Loop End [ALL]")
    d.check("no errors after close", not d.errors, d.errors[:1])
    d.check("open cell got loop end", b.video_params.loop_end is not None)
