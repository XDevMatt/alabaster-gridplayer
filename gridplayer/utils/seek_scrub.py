"""A seek bar dragged along: where to seek to, a few times a second at most.

Every mouse move over the bar held down used to be a seek, and each seek is
a command sent to the cell's own VLC process. At a mouse's rate of moves that
is a flood of them, each turning the one before it down before a picture
comes of it, so the picture stood still until the mouse did. Passed on at
most once an interval, the latest place winning, each seek has the time to
show its frame, and the picture follows the mouse along.

Pure, told the time by its caller, so that it can be tested without a clock.
"""

# how often at most a drag along the bar seeks
SCRUB_INTERVAL_MS = 120


class ScrubThrottle:
    """Where to seek to as the bar is pressed, dragged along and let go.

    Pressed, the bar seeks at once. Dragged, at most once an interval: a
    place come too soon after the last one is kept, the latest only, for
    the caller to ask for again once it is due (see wait_ms, due). Let go,
    the exact place it is let go at, unless the video is already sent there.
    """

    def __init__(self, interval_ms: int = SCRUB_INTERVAL_MS):
        self.interval_ms = interval_ms

        self._is_held = False
        self._sent = None
        self._sent_at = None
        self._pending = None

    @property
    def is_held(self) -> bool:
        return self._is_held

    @property
    def pending(self) -> float | None:
        return self._pending

    def press(self, position: float, now_ms: float) -> float:
        """The bar pressed: gone to at once."""

        self._is_held = True
        self._pending = None
        self._sent = None

        return self._send(position, now_ms)

    def move(self, position: float, now_ms: float) -> float | None:
        """Dragged on: the place to seek to now, or None, the place kept for
        when it is due."""

        self._is_held = True

        if self._sent_at is not None and now_ms - self._sent_at < self.interval_ms:
            self._pending = position
            return None

        return self._send(position, now_ms)

    def wait_ms(self, now_ms: float) -> int | None:
        """How long until the place kept is due; None, with none kept."""

        if self._pending is None:
            return None

        if self._sent_at is None:
            return 0

        return max(0, int(self.interval_ms - (now_ms - self._sent_at)))

    def due(self, now_ms: float) -> float | None:
        """The place kept, if it is due by now."""

        if self._pending is None or self.wait_ms(now_ms):
            return None

        return self._send(self._pending, now_ms)

    def release(self, position: float) -> float | None:
        """Let go: the exact place, unless the video is already sent there,
        or the bar was not being dragged."""

        is_held = self._is_held
        sent = self._sent

        self._reset()

        if not is_held or position == sent:
            return None

        return position

    def abandon(self) -> float | None:
        """Let go somewhere else, where the bar was not told: the place kept,
        for the latest to win still."""

        pending = self._pending

        self._reset()

        return pending

    def _send(self, position: float, now_ms: float) -> float | None:
        self._pending = None

        if position == self._sent:
            return None

        self._sent = position
        self._sent_at = now_ms

        return position

    def _reset(self):
        self._is_held = False
        self._sent = None
        self._sent_at = None
        self._pending = None
