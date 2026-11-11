"""A landscape cell set to skip the other orientation never shuffles to the
portrait clip in its folder, and Off lets it come."""

from gridplayer.params.static import AspectFilter, VideoEndAction
from gridplayer.utils import media_shape


def scenario(d):
    wide = d.media.orientations / "wide1.mp4"
    tall = d.media.orientations / "tall.mp4"

    d.check("tall probed portrait", media_shape.shape_of(tall) is True)
    d.check("wide probed landscape", media_shape.shape_of(wide) is False)

    d.open(wide)
    b = d.wait_for_cell("wide1.mp4")
    d.check(
        "cell is landscape",
        not b.navigation.cell_is_portrait(),
        (b.width(), b.height()),
    )

    d.act(b, "When Finished Shuffle")
    d.ctx.commands.set_cell_profile_field(
        b.video_params.id, "aspect_filter", AspectFilter.REJECT
    )
    d.check("mode set", b.aspect_filter == AspectFilter.REJECT)

    seen = []
    for i in range(6):
        before = b.video_params.uri
        d.act(b, "Play Random File")
        d.wait_until(
            lambda before=before: b.video_params.uri != before, f"shuffle {i + 1} moved"
        )
        d.wait_until(lambda: b.is_playable, f"shuffle {i + 1} plays")
        seen.append(b.video_params.uri.name)
    d.check("never the portrait clip", "tall.mp4" not in seen, seen)

    d.ctx.commands.set_cell_profile_field(
        b.video_params.id, "aspect_filter", AspectFilter.OFF
    )
    seen_off = []
    for i in range(6):
        before = b.video_params.uri
        d.act(b, "Play Random File")
        d.wait_until(
            lambda before=before: b.video_params.uri != before,
            f"off shuffle {i + 1} moved",
        )
        seen_off.append(b.video_params.uri.name)
    d.check("off lets the portrait come", "tall.mp4" in seen_off, seen_off)
    d.check("end action kept", b.video_params.end_action == VideoEndAction.SHUFFLE_FILE)
