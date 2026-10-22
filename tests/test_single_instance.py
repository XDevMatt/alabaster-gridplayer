"""The file-open pipe speaks length-prefixed JSON, never pickle."""

import os
import pickle
import threading
import time
import uuid
from multiprocessing import connection

import pytest

from gridplayer.params import env
from gridplayer.utils import single_instance as si


def test_json_roundtrip_files():
    payload = {"v": 1, "files": ["https://example.com/a.mp4"], "pid": 7}
    encoded = si.encode_message(payload)

    length = int.from_bytes(encoded[:4], "big")
    body = encoded[4:]

    assert length == len(body)
    assert si.decode_message(body) == payload


def test_pickle_payload_is_rejected():
    pickled = pickle.dumps(["C:\\secret\\file.mp4"])

    with pytest.raises(si.ProtocolError, match="pickle"):
        si.decode_message(pickled)


def test_pickle_framed_as_length_is_rejected():
    """An old multiprocessing.connection client writes pickle first."""

    pickled = pickle.dumps(["https://evil.example/x"])

    with pytest.raises(si.ProtocolError):
        si.decode_message(pickled[:4] + pickled)


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"{not json",
        b'"just a string"',
        b"[]",
        b'{"v": 2, "files": []}',
        b"\x80\x04\x95",
    ],
)
def test_malformed_payload_is_rejected(raw):
    with pytest.raises(si.ProtocolError):
        si.decode_message(raw)


def test_files_must_be_a_list_of_strings():
    with pytest.raises(si.ProtocolError, match="list of strings"):
        si.validate_open_items("C:\\Windows\\notepad.exe")

    with pytest.raises(si.ProtocolError, match="list of strings"):
        si.validate_open_items([1, 2])


def test_too_many_files_are_rejected():
    with pytest.raises(si.ProtocolError, match="too many"):
        si.validate_open_items(["https://example.com/a"] * (si.MAX_OPEN_ITEMS + 1))


def test_overlong_path_is_rejected():
    with pytest.raises(si.ProtocolError, match="too long"):
        si.validate_open_items(["https://example.com/" + "a" * si.MAX_ITEM_CHARS])


def test_existing_local_file_is_kept(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"x")

    assert si.validate_open_items([str(video)]) == [str(video)]


def test_existing_directory_is_kept(tmp_path):
    folder = tmp_path / "clips"
    folder.mkdir()

    assert si.validate_open_items([str(folder)]) == [str(folder)]


def test_missing_file_is_dropped(tmp_path):
    missing = tmp_path / "gone.mp4"

    assert si.validate_open_items([str(missing)]) == []


def test_allowed_url_is_kept():
    assert si.validate_open_items(["https://example.com/a.mp4"]) == [
        "https://example.com/a.mp4"
    ]


def test_disallowed_scheme_is_dropped():
    assert si.validate_open_items(["file:///C:/Windows/notepad.exe"]) == []
    assert si.validate_open_items(["smb://host/share/a.mp4"]) == []
    assert si.validate_open_items(["vlc://open"]) == []


def test_payload_larger_than_the_cap_is_rejected():
    with pytest.raises(si.ProtocolError, match="too large"):
        si.encode_message(
            {"v": 1, "files": ["https://x/" + "a" * si.MAX_PAYLOAD_BYTES]}
        )


@pytest.fixture
def isolated_pipe(monkeypatch):
    """A pipe name of our own, so a running player is not in the way."""

    name = rf"\\.\pipe\gridplayer-test-{uuid.uuid4().hex}" if env.IS_WINDOWS else None
    if name:
        monkeypatch.setattr(si, "S_NAME", name)
    return name


@pytest.mark.skipif(not env.IS_WINDOWS, reason="Windows named pipe")
def test_listener_rejects_pickle_on_the_pipe(isolated_pipe, tmp_path):
    listener = si._init_listener()
    assert listener is not None
    assert listener.pipe_mode & si.PIPE_REJECT_REMOTE_CLIENTS

    received = []
    errors = []

    def serve():
        try:
            client = listener.accept()
            with client:
                try:
                    si.decode_message(si._recv_payload(client))
                except si.ProtocolError as e:
                    errors.append(e)
                else:
                    received.append("accepted")
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    time.sleep(0.1)

    client = si._connect_client(isolated_pipe)
    try:
        client.send_all(pickle.dumps(["https://evil.example/a.mp4"]))
    finally:
        client.close()

    thread.join(timeout=5)
    assert errors
    assert received == []


@pytest.mark.skipif(not env.IS_WINDOWS, reason="Windows named pipe")
def test_old_multiprocessing_client_cannot_use_the_pipe(isolated_pipe):
    """The previous pickle framing set message mode, which this pipe refuses."""

    listener = si._init_listener()
    assert listener is not None

    def serve():
        try:
            client = listener.accept()
            client.close()
        except OSError:
            pass
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    time.sleep(0.1)

    try:
        with pytest.raises(OSError, match="parameter is incorrect"):
            connection.Client(isolated_pipe, "AF_PIPE")
    finally:
        listener.close()
        thread.join(timeout=5)


@pytest.mark.skipif(not env.IS_WINDOWS, reason="Windows named pipe")
def test_listener_accepts_json_list_of_real_files(isolated_pipe, tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"x")

    listener = si._init_listener()
    assert listener is not None

    received = []

    def serve():
        try:
            client = listener.accept()
            with client:
                payload = si.decode_message(si._recv_payload(client))
                received.append(si.validate_open_items(payload["files"]))
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    time.sleep(0.1)

    client = si._connect_client(isolated_pipe)
    try:
        si._send_bytes(
            client,
            si.encode_message(
                {"v": 1, "files": [str(video), "vlc://nope"], "pid": os.getpid()}
            ),
        )
    finally:
        client.close()

    thread.join(timeout=5)
    assert received == [[str(video)]]


@pytest.mark.skipif(not env.IS_WINDOWS, reason="Windows named pipe")
def test_listener_rejects_malformed_json_on_the_pipe(isolated_pipe):
    listener = si._init_listener()
    assert listener is not None

    errors = []

    def serve():
        try:
            client = listener.accept()
            with client:
                try:
                    si.decode_message(si._recv_payload(client))
                except si.ProtocolError as e:
                    errors.append(str(e))
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    time.sleep(0.1)

    client = si._connect_client(isolated_pipe)
    try:
        body = b"{not json"
        client.send_all(len(body).to_bytes(4, "big") + body)
    finally:
        client.close()

    thread.join(timeout=5)
    assert errors
