"""A drag along the seek bar: a few seeks a second at most, the latest place
winning, and the exact place it is let go at."""

from types import SimpleNamespace

import pytest
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtTest import QTest

from gridplayer.utils.seek_scrub import SCRUB_INTERVAL_MS, ScrubThrottle
from gridplayer.widgets import video_overlay_elements
from gridplayer.widgets.video_overlay_elements import OverlayProgressBar


class TestScrubThrottle:
    def test_a_press_seeks_at_once(self):
        scrub = ScrubThrottle(100)

        assert scrub.press(0.3, now_ms=0) == 0.3
        assert scrub.is_held

    def test_moves_within_the_interval_are_kept_not_sent(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)

        assert scrub.move(0.2, now_ms=10) is None
        assert scrub.move(0.3, now_ms=50) is None
        assert scrub.pending == 0.3

    def test_the_latest_kept_place_wins_once_due(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)
        scrub.move(0.2, now_ms=10)
        scrub.move(0.25, now_ms=40)
        scrub.move(0.3, now_ms=90)

        assert scrub.wait_ms(now_ms=90) == 10
        assert scrub.due(now_ms=95) is None
        assert scrub.due(now_ms=100) == 0.3
        assert scrub.pending is None
        assert scrub.wait_ms(now_ms=100) is None

    def test_a_move_past_the_interval_is_sent_at_once(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)

        assert scrub.move(0.5, now_ms=100) == 0.5
        assert scrub.move(0.6, now_ms=150) is None
        assert scrub.move(0.7, now_ms=200) == 0.7

    def test_at_most_one_seek_an_interval_however_many_moves(self):
        scrub = ScrubThrottle(100)
        sent = [scrub.press(0.0, now_ms=0)]

        # a mouse polled at 1000Hz dragged across for a second
        for ms in range(1, 1001):
            position = scrub.move(ms / 1000, now_ms=ms)
            due = scrub.due(now_ms=ms)

            sent.extend(p for p in (position, due) if p is not None)

        assert len(sent) <= 1000 // 100 + 1
        assert sent[-1] == 1.0

    def test_the_same_place_is_not_sent_twice(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.4, now_ms=0)

        assert scrub.move(0.4, now_ms=200) is None

    def test_let_go_at_the_exact_place(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)
        scrub.move(0.2, now_ms=10)

        assert scrub.release(0.21) == 0.21
        assert not scrub.is_held
        assert scrub.pending is None

    def test_let_go_where_already_sent_seeks_no_more(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)

        assert scrub.release(0.1) is None

    def test_let_go_without_a_press_is_no_seek(self):
        assert ScrubThrottle(100).release(0.5) is None

    def test_let_go_elsewhere_sends_the_place_kept(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.1, now_ms=0)
        scrub.move(0.6, now_ms=20)

        assert scrub.abandon() == 0.6
        assert not scrub.is_held
        assert scrub.release(0.7) is None

    def test_a_new_press_starts_afresh(self):
        scrub = ScrubThrottle(100)
        scrub.press(0.5, now_ms=0)
        scrub.release(0.5)

        assert scrub.press(0.5, now_ms=10) == 0.5

    def test_the_default_interval_keeps_vlc_from_being_flooded(self):
        assert 80 <= SCRUB_INTERVAL_MS <= 200


@pytest.fixture
def clock(monkeypatch):
    now = SimpleNamespace(ms=1000.0)
    monkeypatch.setattr(video_overlay_elements, "_now_ms", lambda: now.ms)

    return now


@pytest.fixture
def bar():
    bar = OverlayProgressBar()
    bar.setAttribute(Qt.WA_DontShowOnScreen)
    bar.resize(200, 23)

    sent = []
    bar.position_changed.connect(sent.append)
    bar.sent = sent

    yield bar

    bar.close()


class TestSeekBarDrag:
    def test_a_click_seeks_at_once(self, bar, clock):
        QTest.mousePress(bar, Qt.LeftButton, Qt.NoModifier, QPoint(50, 10))

        assert bar.sent == [0.25]

    def test_a_drag_seeks_throttled_and_lands_exactly(self, bar, clock):
        QTest.mousePress(bar, Qt.LeftButton, Qt.NoModifier, QPoint(20, 10))

        for x in range(21, 120):
            clock.ms += 2
            bar._scrub_move(x)

        # about 200 ms of dragging: the press, one more, and one kept
        assert len(bar.sent) <= 3
        assert bar._scrub_timer.isActive()

        QTest.mouseRelease(bar, Qt.LeftButton, Qt.NoModifier, QPoint(150, 10))

        assert bar.sent[-1] == 0.75
        assert not bar._scrub_timer.isActive()

    def test_the_kept_place_goes_when_the_timer_fires(self, bar, clock):
        QTest.mousePress(bar, Qt.LeftButton, Qt.NoModifier, QPoint(20, 10))
        clock.ms += 10
        bar._scrub_move(100)

        assert bar.sent == [0.1]

        clock.ms += SCRUB_INTERVAL_MS
        bar._scrub_due()

        assert bar.sent == [0.1, 0.5]

    def test_a_release_off_the_end_lands_on_the_end(self, bar, clock):
        QTest.mousePress(bar, Qt.LeftButton, Qt.NoModifier, QPoint(20, 10))
        QTest.mouseRelease(bar, Qt.LeftButton, Qt.NoModifier, QPoint(500, 10))

        assert bar.sent == [0.1, 1.0]