"""Which start is the first player, and the others handing it their files
even while it is still starting: Explorer starts one process for each file
picked, all at once."""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from gridplayer.params import env
from gridplayer.utils import single_instance as si

pytestmark = pytest.mark.skipif(env.IS_WINDOWS, reason="the socket and its lock")

# a first player in a process of its own, as the lock is per process: it
# takes the lock, starts listening only after a while (or never, if the
# while is below 0) and prints the one message it is sent
FIRST = """
import json, sys, time
from gridplayer.utils import single_instance as si
si.S_NAME = sys.argv[1]
delay = float(sys.argv[2])
assert si._take_primary_lock()
print("locked", flush=True)
if delay < 0:
    time.sleep(60)
time.sleep(delay)
listener = si._UnixSocketListener(si.S_NAME)
client = listener.accept()
print(json.dumps(si.decode_message(si._recv_payload(client))), flush=True)
"""

# a start that only finds out whether it is the first one, and stays a while
STARTED = """
import sys, time
from gridplayer.utils import single_instance as si
si.S_NAME = sys.argv[1]
print(not si.is_other_instance_running(), flush=True)
time.sleep(2)
"""


@pytest.fixture
def s_name(monkeypatch):
    # short: a socket path has room for about 100 characters
    root = Path(tempfile.mkdtemp(prefix="gp-el-", dir="/tmp"))
    name = str(root / "gridplayer" / "test.socket")
    monkeypatch.setattr(si, "S_NAME", name)
    monkeypatch.setattr(si, "LISTENER", None)
    monkeypatch.setattr(si, "_PRIMARY_LOCK_FD", None)

    yield name

    if si.LISTENER is not None:
        si.LISTENER.close()
    if si._PRIMARY_LOCK_FD is not None:
        os.close(si._PRIMARY_LOCK_FD)
    shutil.rmtree(root, ignore_errors=True)


def _python(script, *args):
    return subprocess.Popen(
        [sys.executable, "-c", script, *map(str, args)],
        stdout=subprocess.PIPE,
        text=True,
    )


def _first(s_name, delay):
    first = _python(FIRST, s_name, delay)
    assert first.stdout.readline().strip() == "locked"
    return first


class TestTheFirstStart:
    def test_is_the_first_player(self, s_name):
        assert si.is_other_instance_running() is False
        assert si.LISTENER is not None

    def test_takes_over_a_socket_left_by_one_that_crashed(self, s_name):
        Path(s_name).parent.mkdir(parents=True)
        left = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        left.bind(s_name)
        left.close()

        assert si.is_other_instance_running() is False
        assert si.LISTENER is not None

    def test_only_one_of_many_started_at_once(self, s_name):
        starts = [_python(STARTED, s_name) for _ in range(8)]

        firsts = [start.stdout.readline().strip() for start in starts]
        for start in starts:
            start.wait(timeout=30)

        assert firsts.count("True") == 1, firsts


class TestASecondStart:
    def test_hands_its_files_to_a_first_still_starting(self, s_name, tmp_path):
        video = tmp_path / "a.mp4"
        video.touch()
        first = _first(s_name, 1.0)

        try:
            assert si.is_delegated_to_primary(["gridplayer", str(video)]) is True
            message = json.loads(first.stdout.readline())
        finally:
            first.kill()
            first.wait()

        assert message["files"] == [str(video)]

    def test_does_not_take_a_first_still_starting_for_none(self, s_name):
        first = _first(s_name, -1)

        try:
            assert si.is_other_instance_running() is True
            assert si.LISTENER is None
            assert Path(f"{s_name}.lock").exists()
        finally:
            first.kill()
            first.wait()

    def test_gives_up_on_one_that_never_listens(self, s_name):
        first = _first(s_name, -1)

        try:
            started = time.monotonic()
            assert si.is_delegated_to_primary(["gridplayer"], timeout=0.5) is False
            took = time.monotonic() - started
        finally:
            first.kill()
            first.wait()

        assert took < 3

    def test_is_the_first_once_the_first_is_gone(self, s_name):
        first = _first(s_name, -1)
        first.kill()
        first.wait()

        assert si.is_other_instance_running() is False
