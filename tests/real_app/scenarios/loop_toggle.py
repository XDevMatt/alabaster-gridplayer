"""Shift+L flips a cell to Loop This File and back to its own end action;
[ and ] set the A-B loop marks like , and ."""

from gridplayer.models.playlist import Playlist
from gridplayer.models.video import VideoEndAction
from gridplayer.params.actions import ACTIONS


def scenario(d):
    acts = ACTIONS
    d.check("Shift+L bound", acts["Toggle Loop File"].get("key") == "Shift+L")
    d.check("[ sets start", "[" in acts["Set Loop Start"].get("keys", ()))
    d.check("] sets end", "]" in acts["Set Loop End"].get("keys", ()))

    d.open(d.media.feature)
    b = d.wait_for_cell("feature.mkv")

    d.act(b, "When Finished Shuffle")
    d.wait_until(lambda: b.video_params.end_action == VideoEndAction.SHUFFLE_FILE, "shuffle set")

    d.act(b, "Toggle Loop File")
    d.wait_until(lambda: b.video_params.end_action == VideoEndAction.LOOP_FILE, "loop on")

    text = Playlist(videos=[b.video_params]).dumps()
    saved = Playlist.parse(text).videos[0]
    d.check("saved loop", saved.end_action == VideoEndAction.LOOP_FILE)
    d.check("saved before", saved.end_action_before_loop == VideoEndAction.SHUFFLE_FILE)

    d.act(b, "Toggle Loop File")
    d.wait_until(lambda: b.video_params.end_action == VideoEndAction.SHUFFLE_FILE, "back to shuffle")
    d.check("before cleared", b.video_params.end_action_before_loop is None)


