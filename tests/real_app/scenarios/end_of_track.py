"""The end of a file with When Finished set to Next, Shuffle or Loop.

Next and Shuffle go straight on to another file of the folder: the file
that ended must not start over, not even for a moment, before the next one
loads (the end-of-track blip). Loop This File goes round in place, with no
reload.

The folder has to hold two files or more, or Next has nowhere to go. Set
GRIDPLAYER_BLIP_MOVIES to a folder of real movies to run it on those (the
Windows check uses three Blender open movies, two of them about ten minutes
long); without it, the folder of generated clips is used. The time VLC
reports for each file is written down as it comes, straight from that
file's player before the cell hears it, so a replay shows even where the
cell lets the player go on hearing it.
"""

import os
import time
from pathlib import Path

from gridplayer.params.static import VideoEndAction

# how far before the end a long file is played from
LEAD_MS = 5_000

# a time this far into the file, once it was near the end, is a replay
REPLAY_FRACTION = 0.5

VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


def _files(d) -> list[Path]:
    folder = os.environ.get("GRIDPLAYER_BLIP_MOVIES")
    root = Path(folder) if folder else d.media.folder
    return sorted(
        (p for p in root.iterdir() if p.suffix.lower() in VIDEO_SUFFIXES),
        key=lambda p: p.name.lower(),
    )


class Recorder:
    """Every time each player of a cell reports, with the file it plays."""

    def __init__(self, d, block):
        self.d = d
        self.block = block
        self.reports: list[tuple[int, str, int]] = []
        self._drivers: dict[int, object] = {}

    def follow(self):
        driver = self.block.video_driver
        if driver is None or id(driver) in self._drivers:
            return

        # From the player inside the cell's frame, which the frame passes on
        # to the cell: the cell lets the frame go as soon as it acts on a
        # time, taking every other listener of that very report with it
        source = getattr(driver, "video_driver", driver)
        if source is None:
            return

        self._drivers[id(driver)] = driver
        number = len(self._drivers)
        name = self.block.video_params.uri.name

        source.time_changed.connect(
            lambda t, n=number, f=name: self.reports.append((n, f, int(t)))
        )

    def pump_until(self, predicate, what, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.follow()
            try:
                if predicate():
                    return True
            except Exception:
                pass
            self.d.pump(0.01)
        self.d.fail(f"gave up after {timeout}s waiting until {what}")
        return False

    def of_driver(self, number):
        return [t for n, _f, t in self.reports if n == number]

    @property
    def driver_number(self):
        return len(self._drivers)


def _replays(times: list[int], length: int) -> list[int]:
    """The times reported after the end was near that are back in the
    first part of the file."""

    near = next((i for i, t in enumerate(times) if t >= length - 3_000), None)
    if near is None:
        return []
    return [t for t in times[near:] if t < length * REPLAY_FRACTION]


def _play_out(d, rec, block, end_action, label, seek_near_end=True, timeout=120):
    """Play the cell's file to its end with this end action; the file it
    went on to."""

    d.act(block, end_action)
    rec.follow()
    number = rec.driver_number
    name = block.video_params.uri.name
    length = block.video_driver.length

    if seek_near_end and length > LEAD_MS * 2:
        block.seek(length - LEAD_MS)

    went_on = rec.pump_until(
        lambda: block.video_params.uri.name != name and block.is_playable,
        f"{label}: {name} ends and the next file plays",
        timeout=timeout,
    )

    times = rec.of_driver(number)
    replays = _replays(times, length)
    d.check(
        f"{label}: {name} reached its end",
        any(t >= length - 3_000 for t in times),
        times[-5:],
    )
    d.check(
        f"{label}: {name} did not start over before the next file",
        not replays,
        {"replayed_times": replays[:10], "length": length, "last": times[-8:]},
    )
    d.note(f"{label}: now on {block.video_params.uri.name}", block)

    return went_on


def scenario(d):
    files = _files(d)
    d.check("a folder of two files or more", len(files) >= 2, [f.name for f in files])
    if len(files) < 2:
        return

    d.open(files[0])
    block = d.wait_for_cell(files[0].name, timeout=60)
    rec = Recorder(d, block)
    rec.follow()

    # Next: the first file goes on to the second. It was opened under the
    # default, Loop This File, so this is the end action changed mid-file
    _play_out(d, rec, block, "When Finished Next", "Next")
    d.check("Next: on the second file", block.video_params.uri == files[1])

    # Shuffle: on to another file, not the one that ended
    before = block.video_params.uri
    _play_out(d, rec, block, "When Finished Shuffle", "Shuffle")
    d.check("Shuffle: on another file", block.video_params.uri != before)

    # the last file of the folder goes round to the first, played whole if
    # it is short (the Sintel trailer, 52s), from near its end if not
    while block.video_params.uri != files[-1]:
        name = block.video_params.uri.name
        d.act(block, "Play Next File")
        rec.pump_until(
            lambda n=name: block.video_params.uri.name != n and block.is_playable,
            "stepped on",
            timeout=60,
        )
    is_short = block.video_driver.length <= 90_000
    _play_out(
        d,
        rec,
        block,
        "When Finished Next",
        "Last to first",
        seek_near_end=not is_short,
    )
    d.check("Last to first: on the first file", block.video_params.uri == files[0])

    # Loop This File, set on a file opened to move on, goes round in place
    # with the same player
    d.act(block, "When Finished Loop File")
    d.wait_until(
        lambda: block.video_params.end_action == VideoEndAction.LOOP_FILE, "loop on"
    )
    _goes_round(d, rec, block, "Loop (set mid-file)")

    # a file opened under Loop This File goes round the same way, VLC's own
    # wrap
    name = block.video_params.uri.name
    d.act(block, "Play Next File")
    rec.pump_until(
        lambda: block.video_params.uri.name != name and block.is_playable,
        "on to a file opened to loop",
        timeout=60,
    )
    _goes_round(d, rec, block, "Loop (opened looping)")

    # and set to Next while it plays, it goes on with no replay all the same
    _play_out(d, rec, block, "When Finished Next", "Next (Loop off mid-file)")


def _goes_round(d, rec, block, label):
    rec.follow()
    number = rec.driver_number
    name = block.video_params.uri.name
    length = block.video_driver.length
    block.seek(length - LEAD_MS)

    def wrapped_and_on():
        times = rec.of_driver(number)
        near = next((i for i, t in enumerate(times) if t >= length - 3_000), None)
        if near is None:
            return False
        after = [t for t in times[near:] if t < length * REPLAY_FRACTION]
        return bool(after) and max(after) >= 2_000

    rec.pump_until(wrapped_and_on, f"{label}: back at the start and playing on", 60)
    d.check(f"{label}: went round", wrapped_and_on(), rec.of_driver(number)[-8:])
    d.check(f"{label}: same file", block.video_params.uri.name == name)
    d.check(f"{label}: same player, no reload", rec.driver_number == number)
    d.check(f"{label}: still playing", not block.video_params.is_paused)
