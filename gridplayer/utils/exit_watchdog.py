"""The last word on closing: once the player has decided to close, it is
gone within EXIT_WATCHDOG_S seconds, whatever got stuck on the way out.

Closing hides the window first and then tears everything down. Anything in
that teardown that never returns (a pipe read, a thread join, a process
wait) would otherwise leave the process running with no window, for good.
The watchdog is a daemon thread, so it never keeps the process alive
itself.
"""

import contextlib
import logging
import os
import threading
import time
from multiprocessing import active_children

EXIT_WATCHDOG_S = 10.0
# how long a decoder process gets to go after it is asked to, before it is
# killed outright
CHILD_TERMINATE_GRACE_S = 0.5
WATCHDOG_EXIT_CODE = 1

_log = logging.getLogger(__name__)

_lock = threading.Lock()
_armed: threading.Event | None = None


def arm(timeout: float = EXIT_WATCHDOG_S, on_fire=None) -> threading.Event:
    """Start the countdown, once: arming again keeps the first one.

    Setting the returned event calls it off. on_fire is what happens when it
    runs out, the process taken down by default.
    """

    global _armed

    with _lock:
        if _armed is not None:
            return _armed

        cancelled = threading.Event()
        _armed = cancelled

    fire = on_fire or force_exit

    def watch():
        if not cancelled.wait(timeout):
            fire()

    threading.Thread(target=watch, name="exit-watchdog", daemon=True).start()

    return cancelled


def disarm() -> None:
    """Call the countdown off, and let arm start a new one."""

    global _armed

    with _lock:
        armed, _armed = _armed, None

    if armed is not None:
        armed.set()


def force_exit() -> None:
    """Take down every child process, then this one, now."""

    # nothing may stop the exit, a log that cannot be written least of all
    with contextlib.suppress(Exception):
        _log.critical(
            f"Still not closed {EXIT_WATCHDOG_S:g} s after closing began,"
            " forcing the exit"
        )
        for handler in logging.getLogger().handlers:
            handler.flush()

    try:
        kill_children()
    finally:
        os._exit(WATCHDOG_EXIT_CODE)


def kill_children(grace: float = CHILD_TERMINATE_GRACE_S) -> None:
    """Ask every child process to go, and kill the ones still there after
    grace seconds."""

    children = active_children()

    for child in children:
        _quietly(child.terminate)

    deadline = time.monotonic() + grace

    for child in children:
        _quietly(child.join, timeout=max(0.0, deadline - time.monotonic()))
        _quietly(_kill_if_alive, child)


def _kill_if_alive(child) -> None:
    if child.is_alive():
        child.kill()


def _quietly(func, *args, **kwargs) -> None:
    # a child already reaped, or closed, is no reason to stop
    with contextlib.suppress(OSError, ValueError, AssertionError):
        func(*args, **kwargs)
