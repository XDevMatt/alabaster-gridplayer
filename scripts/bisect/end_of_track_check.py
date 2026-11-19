"""Bisect check: does a cell whose When Finished is Next File act before its
file ends, or only after VLC has started the file over?

Plays file 1 of a two-file folder (a.mp4, b.mp4) to its end as VLC reports
it: time every 250 ms up to the end, then the time falling back to near 0,
which is what VLC reports once it starts the same input again (playlist
repeat in old builds, :input-repeat in new ones). The cell's real
time_changed logic runs on each report; the navigation is a recording fake.

exit 0 (good): the end action ran before the time reached the end.
exit 1 (bad):  the end action ran only after the time fell back to the start
               (the replay of the start of file 1 before file 2).
exit 125: this commit cannot be checked.
"""

import os
import sys
import tempfile
from functools import partial
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from gridplayer.models.video import Video
    from gridplayer.params.static import VideoEndAction
    from gridplayer.widgets.video_block import VideoBlock
except Exception as e:  # noqa: BLE001
    print("SKIP: cannot import", repr(e))
    sys.exit(125)

LENGTH = 10_000
folder = Path(tempfile.mkdtemp())
for name in ("a.mp4", "b.mp4"):
    (folder / name).write_bytes(b"\0")

block = mock.Mock()
block.video_params = Video(uri=folder / "a.mp4", end_action=VideoEndAction.NEXT_FILE)
block.video_driver.length = LENGTH
block.is_video_initialized = True
block.is_live = False
block.is_stopped = False
block._last_time = None
block._seek_target = None
block._seek_settle_timer.isActive.return_value = False
block._follow_seek = lambda t: False
block.bookmarker.is_editing = False

for name in ("_is_loop_wrapped", "_loop_wrapped"):
    if hasattr(VideoBlock, name):
        setattr(block, name, partial(getattr(VideoBlock, name), block))

block.loop_start = VideoBlock.loop_start.fget(block)
block.loop_end = VideoBlock.loop_end.fget(block)

events = []
block.loop_end_action.side_effect = lambda: events.append(("end_action", block.time))

time_changed = getattr(VideoBlock.time_changed, "__wrapped__", VideoBlock.time_changed)

reports = [*range(0, LENGTH - 40, 250), LENGTH - 40, 120, 370, 620]
for t in reports:
    if events:
        break
    time_changed(block, t)

print("loop_end:", block.loop_end, "events:", events)

if not events:
    print("BAD: no end action at all")
    sys.exit(1)

_, at = events[0]
if at >= LENGTH / 2:
    print(f"GOOD: end action at {at} ms, before the end")
    sys.exit(0)

print(f"BAD: end action only after the time fell back to {at} ms (start replayed)")
sys.exit(1)
