"""Closing the player ends the process, whatever is stuck on the way out.

Each of these hung for good before: the instance pipe waiting on a client
that never wrote, the process manager's loop and waits, the log listener,
and nothing at all to fall back on when the rest of it did.
"""

import contextlib
import logging
import os
import socket
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
from multiprocessing import Value
from pathlib import Path
from queue import Queue
from unittest.mock import MagicMock

import pytest
from PyQt5.QtWidgets import QWidget

from gridplayer.multiprocess.command_loop import CommandLoopThreaded
from gridplayer.multiprocess.process_manager import ProcessManager
from gridplayer.params import env
from gridplayer.player.manager import Commands, Context
from gridplayer.player.managers import window_state as window_state_module
from gridplayer.player.managers.window_state import WindowStateManager
from gridplayer.utils import exit_watchdog
from gridplayer.utils import single_instance as si
from gridplayer.utils.log_config import QueueListenerRoot

# what a test lets a step take before calling it a hang
HANG_S = 6.0


def _in_time(func, *args):
    """How long func took, or None when it was still going after HANG_S."""

    done = []

    def run():
        start = time.monotonic()
        func(*args)
        done.append(time.monotonic() - start)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(HANG_S)

    return done[0] if done else None


# the instance pipe


@pytest.fixture
def unix_pipe(monkeypatch):
    if env.IS_WINDOWS:
        pytest.skip("the Unix socket; the named pipe has tests of its own")

    # short: a Unix socket path has a limit of about 100 bytes
    where = Path(tempfile.mkdtemp(prefix="gp-si-"))
    monkeypatch.setattr(si, "S_NAME", str(where / "s.socket"))
    listener = si._init_listener()
    assert listener is not None
    monkeypatch.setattr(si, "LISTENER", listener)

    yield si.S_NAME

    listener.close()


def _silent_client(path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(path)
    return sock


class TestTheInstancePipe:
    def test_a_client_that_never_writes_does_not_hang_closing(self, unix_pipe):
        listener = si.Listener()
        listener.start()
        silent = _silent_client(unix_pipe)
        time.sleep(0.1)

        try:
            took = _in_time(listener.cleanup)
        finally:
            silent.close()

        assert took is not None, "closing waited on the silent client for good"
        assert took < si.CLIENT_READ_TIMEOUT_S + si.LISTENER_JOIN_TIMEOUT_S + 1
        assert not listener._thread.is_alive()

    def test_the_next_client_is_still_heard(self, unix_pipe, mocker):
        listener = si.Listener()
        heard = mocker.patch.object(listener, "_handle_input_data")
        listener.start()
        silent = _silent_client(unix_pipe)

        try:
            si._send_payload({"v": si.PROTOCOL_VERSION, "cmd": si.CMD_PING})

            deadline = time.monotonic() + HANG_S
            while not heard.called and time.monotonic() < deadline:
                time.sleep(0.05)
        finally:
            silent.close()
            listener.cleanup()

        heard.assert_called_once_with(si.CMD_PING)

    def test_closing_goes_on_when_the_listener_cannot_be_told(self, unix_pipe, mocker):
        listener = si.Listener()
        listener.start()
        mocker.patch.object(si, "_send_payload", side_effect=OSError("gone"))

        took = _in_time(listener.cleanup)

        assert took is not None
        assert took < si.LISTENER_JOIN_TIMEOUT_S + 1

    def test_a_client_gives_up_on_a_socket_nobody_serves(self, monkeypatch):
        if env.IS_WINDOWS:
            pytest.skip("Unix socket")

        where = Path(tempfile.mkdtemp(prefix="gp-si-"))
        path = str(where / "s.socket")
        # bound and listening with a backlog that is soon full, never accepted
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(path)
        server.listen(0)
        fillers = []

        def connect_many():
            # the first few fill the backlog, the next one has to give up
            with contextlib.suppress(OSError):
                fillers.extend(si._connect_client(path) for _ in range(64))

        try:
            took = _in_time(connect_many)
        finally:
            for client in fillers:
                client.close()
            server.close()

        assert took is not None, "a client waited for good"


class TestReadingThePipe:
    """The Windows pipe's read, which a synchronous ReadFile cannot bound."""

    def test_nothing_sent_is_given_up_on(self):
        start = time.monotonic()

        with pytest.raises(TimeoutError):
            si._read_pipe_exact(lambda: 0, lambda k: b"", 4, timeout=0.2)

        assert time.monotonic() - start < 1.0

    def test_what_comes_in_pieces_is_put_together(self):
        pieces = [b"", b"ab", b"", b"cd"]
        buffer = bytearray()

        def peek():
            if pieces:
                buffer.extend(pieces.pop(0))
            return len(buffer)

        def read(k):
            out = bytes(buffer[:k])
            del buffer[:k]
            return out

        assert si._read_pipe_exact(peek, read, 4, timeout=2) == b"abcd"

    def test_a_client_gone_is_the_end(self):
        def peek():
            raise EOFError

        with pytest.raises(EOFError):
            si._read_pipe_exact(peek, lambda k: b"", 4, timeout=2)

    def test_a_read_of_nothing_is_the_end(self):
        with pytest.raises(EOFError):
            si._read_pipe_exact(lambda: 4, lambda k: b"", 4, timeout=2)


@pytest.mark.skipif(not env.IS_WINDOWS, reason="Windows named pipe")
class TestTheNamedPipe:
    @pytest.fixture
    def pipe_name(self, monkeypatch):
        import uuid

        name = rf"\\.\pipe\gridplayer-test-{uuid.uuid4().hex}"
        monkeypatch.setattr(si, "S_NAME", name)
        return name

    def test_a_client_that_never_writes_is_dropped(self, pipe_name):
        listener = si._init_listener()
        errors = []

        def serve():
            try:
                client = listener.accept()
                with client:
                    try:
                        si._recv_payload(client)
                    except OSError as e:
                        errors.append(e)
            finally:
                listener.close()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        time.sleep(0.1)

        silent = si._connect_client(pipe_name)
        try:
            thread.join(HANG_S)
        finally:
            silent.close()

        assert not thread.is_alive()
        assert isinstance(errors[0], TimeoutError)

    def test_a_client_gives_up_on_a_busy_pipe(self, pipe_name):
        listener = si._init_listener()
        # the one instance taken, and no next one made: nobody accepts
        first = si._connect_client(pipe_name)

        try:
            start = time.monotonic()
            # ERROR_SEM_TIMEOUT, as WaitNamedPipe runs out
            with pytest.raises(OSError):  # noqa: PT011
                si._connect_client(pipe_name)
            took = time.monotonic() - start
        finally:
            first.close()
            listener.close()

        assert took < si.CLIENT_CONNECT_TIMEOUT_S + 2


# the decoder process manager


class _Stuck(CommandLoopThreaded):
    loop_thread_daemon = True
    loop_join_timeout = 0.3

    def __init__(self):
        super().__init__()
        self.release = threading.Event()

    def stick(self):
        self.release.wait()


class TestTheProcessManager:
    def test_its_loop_does_not_keep_the_process_alive(self):
        assert ProcessManager.loop_thread_daemon is True
        assert ProcessManager.loop_join_timeout is not None
        assert ProcessManager.loop_join_timeout <= 5

    def test_a_loop_stuck_on_a_command_does_not_hang_closing(self):
        loop = _Stuck()
        loop.cmd_loop_start_thread()
        loop.cmd_send_self("stick")
        time.sleep(0.1)

        try:
            took = _in_time(loop.cmd_loop_terminate)
            assert took is not None, "terminating waited on the loop for good"
            assert loop._thread.daemon
        finally:
            loop.release.set()

    def test_the_other_loops_are_left_as_they_were(self):
        assert CommandLoopThreaded.loop_thread_daemon is False
        assert CommandLoopThreaded.loop_join_timeout is None

    def test_a_process_that_will_not_be_reaped_does_not_hang_it(self):
        manager = ProcessManager.__new__(ProcessManager)
        manager.instances_lock = threading.Lock()
        manager.instances = {}
        manager._exiting_instances = {}
        manager._crash_listeners = {}
        manager._is_shutting_down = True
        manager._instances_killed = threading.Condition()
        manager._log = logging.getLogger("test")

        never = threading.Event()
        process = MagicMock()
        process.join.side_effect = lambda timeout=None: never.wait(timeout)
        process.exitcode = None
        instance = MagicMock(id=1, process=process, is_dead=Value("i", 0))

        took = _in_time(manager._process_exited, instance)

        assert took is not None, "reaping waited on the process for good"
        process.close.assert_not_called()


class _Blocking(logging.Handler):
    def __init__(self):
        super().__init__()
        self.release = threading.Event()

    def handle(self, record):
        self.release.wait()
        return True


class TestTheLogListener:
    def test_a_handler_that_never_returns_does_not_hang_stopping(self):
        queue = Queue()
        listener = QueueListenerRoot(queue)
        handler = _Blocking()
        listener.handlers = (handler,)
        listener.respect_handler_level = False
        listener.start()
        queue.put(logging.makeLogRecord({"msg": "x", "levelno": logging.CRITICAL}))
        time.sleep(0.1)

        try:
            took = _in_time(lambda: listener.stop(timeout=0.3))
        finally:
            handler.release.set()

        assert took is not None, "stopping waited on the handler for good"
        assert took < 2


# the watchdog


class TestTheWatchdog:
    def test_it_goes_off_when_closing_takes_too_long(self):
        fired = threading.Event()

        exit_watchdog.arm(timeout=0.1, on_fire=fired.set)

        assert fired.wait(2)

    def test_called_off_it_stays_quiet(self):
        fired = threading.Event()

        exit_watchdog.arm(timeout=0.3, on_fire=fired.set)
        exit_watchdog.disarm()

        assert not fired.wait(0.6)

    def test_arming_again_keeps_the_first_countdown(self):
        first = exit_watchdog.arm(timeout=5, on_fire=lambda: None)

        assert exit_watchdog.arm(timeout=5, on_fire=lambda: None) is first

    def test_it_waits_ten_seconds(self):
        assert exit_watchdog.EXIT_WATCHDOG_S == 10.0

    def test_it_takes_the_process_and_its_children_down(self, tmp_path):
        """For real, in a process of its own that hangs on its way out."""

        pid_file = tmp_path / "child.pid"
        script = tmp_path / "hang.py"
        script.write_text(
            textwrap.dedent(
                f"""
                import multiprocessing, threading, time
                from pathlib import Path

                def child():
                    time.sleep(120)

                if __name__ == "__main__":
                    ctx = multiprocessing.get_context("spawn")
                    p = ctx.Process(target=child)
                    p.start()
                    Path({str(pid_file)!r}).write_text(str(p.pid))

                    from gridplayer.utils import exit_watchdog
                    exit_watchdog.arm(timeout=1.0)

                    # stuck for good, as a join on a thread that never ends is
                    threading.Event().wait()
                """
            )
        )

        start = time.monotonic()
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=Path(__file__).resolve().parent.parent,
            timeout=30,
            check=False,
        )
        took = time.monotonic() - start

        assert result.returncode == exit_watchdog.WATCHDOG_EXIT_CODE
        assert took < 15

        child_pid = int(pid_file.read_text())
        assert not _is_running(child_pid), "the child was left behind"


def _is_running(pid: int) -> bool:
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        # a zombie of ours is reaped by init once its parent is gone
        try:
            status = Path(f"/proc/{pid}/status").read_text()
        except OSError:
            return False
        if "\nState:\tZ" in status:
            return False
        time.sleep(0.1)
    return True


class TestClosingArmsIt:
    def _manager(self, commands):
        window = QWidget()
        ctx = Context()
        ctx.commands = Commands()
        ctx.commands.update(commands)
        return WindowStateManager(context=ctx, parent=window), window

    def test_closing_starts_the_countdown_before_tearing_down(self, mocker):
        mocker.patch.object(window_state_module, "force_terminate")
        events = []
        arm = mocker.patch.object(
            exit_watchdog, "arm", side_effect=lambda: events.append("arm")
        )
        manager, window = self._manager(
            {
                "check_playlist_save": lambda: (events.append("ask"), True)[1],
                "remember_last_playlist": lambda: events.append("remember"),
                "force_close_playlist": lambda: events.append("close"),
            }
        )
        mocker.patch.object(window, "hide", side_effect=lambda: events.append("hide"))

        manager.closeEvent(MagicMock())

        arm.assert_called_once()
        assert events == ["ask", "arm", "remember", "hide", "close"]

    def test_not_while_the_user_is_asked_or_says_no(self, mocker):
        mocker.patch.object(window_state_module, "force_terminate")
        arm = mocker.patch.object(exit_watchdog, "arm")
        manager, _ = self._manager(
            {
                "check_playlist_save": lambda: False,
                "remember_last_playlist": MagicMock(),
                "force_close_playlist": MagicMock(),
            }
        )

        manager.closeEvent(MagicMock())

        arm.assert_not_called()
