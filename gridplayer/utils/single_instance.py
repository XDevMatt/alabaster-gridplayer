import contextlib
import json
import logging
import os
import socket
import stat
import threading
import time
from pathlib import Path
from threading import Thread

from PyQt5.QtCore import QObject, pyqtSignal

from gridplayer.models.video_uri import URL_ALLOWED_SCHEMES, URL_MAX_LENGTH
from gridplayer.params import env
from gridplayer.utils.misc import is_remote_share
from gridplayer.version import __instance_name__

# the fork's own name, so upstream GridPlayer and the fork never take each
# other's files; do not revert when merging upstream
if env.IS_WINDOWS:
    S_NAME = f"\\\\.\\pipe\\{__instance_name__}"
elif env.IS_FLATPAK:
    S_NAME = str(env.FLATPAK_RUNTIME_DIR / f"{__instance_name__}.socket")
elif os.getenv("XDG_RUNTIME_DIR"):
    S_NAME = f"{os.environ['XDG_RUNTIME_DIR']}/gridplayer/{__instance_name__}.socket"
else:
    S_NAME = None

PROTOCOL_VERSION = 1
MAX_PAYLOAD_BYTES = 1 * 1024 * 1024
MAX_OPEN_ITEMS = 1024
MAX_ITEM_CHARS = max(URL_MAX_LENGTH, 32 * 1024)
LENGTH_BYTES = 4

# pickle protocol opcodes start with 0x80; a client still speaking the old
# multiprocessing.connection framing is rejected before json.loads
PICKLE_PREFIX = 0x80

CMD_PING = "ping"
CMD_SHUTDOWN = "shutdown"

# How long the listener waits for a client that connected to send its
# message. One that connects and says nothing (a second start that died
# half way) would otherwise hold the listener, and with it the exit, for
# good: the shutdown message queues up behind it unread.
CLIENT_READ_TIMEOUT_S = 1.0
# how long a client waits for the pipe to take it, and for its message to go
CLIENT_CONNECT_TIMEOUT_S = 2.0
# how long closing waits for the listener to stop; it is a daemon thread, so
# one still stuck after this does not keep the process alive
LISTENER_JOIN_TIMEOUT_S = 2.0
# how often a pipe read looks for bytes while it waits for them
PIPE_POLL_S = 0.01

_log = logging.getLogger(__name__)

if env.IS_MACOS:
    from Foundation import NSWorkspace

    from gridplayer.version import __app_id__

    def is_the_only_instance():
        instances_count = sum(
            app.bundleIdentifier() == __app_id__
            for app in NSWorkspace.sharedWorkspace().runningApplications()
        )

        return instances_count == 1

else:

    def is_the_only_instance():
        """Dummy"""


LISTENER = None


class ProtocolError(ValueError):
    """Bytes on the instance pipe that are not a v1 JSON message."""


def encode_message(payload: dict) -> bytes:
    """Length-prefixed UTF-8 JSON, the only thing this pipe speaks."""

    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )

    if len(body) > MAX_PAYLOAD_BYTES:
        raise ProtocolError("payload too large")

    return len(body).to_bytes(LENGTH_BYTES, "big") + body


def decode_message(data: bytes) -> dict:
    """The JSON object after the 4-byte length, or ProtocolError."""

    if not data:
        raise ProtocolError("empty payload")

    if data[0] == PICKLE_PREFIX:
        raise ProtocolError("pickle is not accepted")

    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ProtocolError("not JSON") from e

    if not isinstance(payload, dict):
        raise ProtocolError("message must be a JSON object")

    if payload.get("v") != PROTOCOL_VERSION:
        raise ProtocolError("unsupported protocol version")

    return payload


def validate_open_items(items) -> list[str]:
    """Paths and URLs the player may open from another instance.

    Anything else is dropped: a random local process used to be able to
    push an arbitrary string into the running player.
    """

    if not isinstance(items, list):
        raise ProtocolError("files must be a list of strings")

    if len(items) > MAX_OPEN_ITEMS:
        raise ProtocolError("too many files")

    accepted = []

    for item in items:
        if not isinstance(item, str):
            raise ProtocolError("files must be a list of strings")

        if len(item) > MAX_ITEM_CHARS:
            raise ProtocolError("path too long")

        if _is_allowed_open_item(item):
            accepted.append(item)

    return accepted


def _is_allowed_open_item(item: str) -> bool:
    if "://" in item:
        scheme = item.split("://", 1)[0].lower()
        return scheme in URL_ALLOWED_SCHEMES

    # not even looked at: another process could have the player log in to
    # any computer, see is_remote_share
    if is_remote_share(item):
        return False

    path = Path(item)

    try:
        return path.exists() and (path.is_file() or path.is_dir())
    except OSError:
        return False


def _init_listener():
    if not S_NAME:
        return None

    try:
        if env.IS_WINDOWS:
            return _WindowsPipeListener(S_NAME)
        return _UnixSocketListener(S_NAME)
    except OSError as e:
        _log.debug(
            "Couldn't start single instance listener,"
            " probably other process is using it: %s",
            e,
        )

    return None


class Listener(QObject):
    open_files = pyqtSignal(list)
    # started again, with files or without: the window is to be shown
    activate = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._log = logging.getLogger(self.__class__.__name__)

        self._thread = None

    def start(self):
        if LISTENER is None:
            self._log.warning("Couldn't start single instance listener")
            return

        self._thread = Thread(target=self._listen, args=(LISTENER,), daemon=True)
        self._thread.start()

    def cleanup(self):
        if self._thread is None or not self._thread.is_alive():
            return

        self._log.debug("Terminating instance socket")

        try:
            _send_payload({"v": PROTOCOL_VERSION, "cmd": CMD_SHUTDOWN})
        except OSError as e:
            self._log.warning(f"Couldn't tell the instance listener to stop: {e}")

        self._thread.join(timeout=LISTENER_JOIN_TIMEOUT_S)

        if self._thread.is_alive():
            self._log.warning("Instance listener did not stop, leaving it behind")

    def _listen(self, listener):
        self._log.debug(f"Instance socket listening at {S_NAME}")

        self._listening_loop(listener)

        listener.close()

    def _listening_loop(self, listener):
        while True:
            try:
                client = listener.accept()
            except OSError:
                break

            with client:
                try:
                    payload = decode_message(_recv_payload(client))
                except (EOFError, OSError, ProtocolError) as e:
                    self._log.debug(f"Rejected instance payload: {e}")
                    continue

            cmd = payload.get("cmd")

            if cmd == CMD_SHUTDOWN:
                break

            if cmd == CMD_PING:
                self._handle_input_data(CMD_PING)
                continue

            try:
                files = validate_open_items(payload.get("files", []))
            except ProtocolError as e:
                self._log.debug(f"Rejected instance files: {e}")
                continue

            self._handle_input_data(files)

    def _handle_input_data(self, input_data):
        if input_data == CMD_PING:
            self._log.debug("Received ping from another instance")
            return

        if not isinstance(input_data, list):
            return

        self.activate.emit()

        if input_data:
            self.open_files.emit(input_data)


def _send_payload(payload: dict) -> None:
    _log.debug(f"Sending data to running instance: {payload.get('cmd') or 'files'}")

    client = _connect_client(S_NAME)
    try:
        _send_bytes(client, encode_message(payload))
    finally:
        client.close()


def _send_data(output_data):
    """Back-compat for tests that still call the old name with a list or ping."""

    if output_data is None:
        _send_payload({"v": PROTOCOL_VERSION, "cmd": CMD_SHUTDOWN})
        return

    if output_data == CMD_PING:
        _send_payload({"v": PROTOCOL_VERSION, "cmd": CMD_PING})
        return

    _send_payload(
        {
            "v": PROTOCOL_VERSION,
            "files": list(output_data),
            "pid": os.getpid(),
        }
    )


def _is_socket_working():
    s_path = Path(S_NAME)
    s_path.parent.mkdir(parents=True, exist_ok=True)

    if s_path.exists():
        if not stat.S_ISSOCK(s_path.stat().st_mode):
            s_path.unlink()
            return False

        try:
            _send_payload({"v": PROTOCOL_VERSION, "cmd": CMD_PING})
        except (ConnectionRefusedError, FileNotFoundError, OSError):
            s_path.unlink()
            return False

        _log.debug("Socket already exists and responding")
        return True

    return False


def is_other_instance_running():
    global LISTENER

    if env.IS_LINUX and _is_socket_working():
        return True

    LISTENER = _init_listener()

    return LISTENER is None


def is_delegated_to_primary(argv):
    if not is_other_instance_running():
        return False

    try:
        client = _connect_client(S_NAME)
    except (FileNotFoundError, ConnectionRefusedError, OSError):
        return False

    try:
        _allow_foreground(_peer_pid(client))
        _send_bytes(
            client,
            encode_message(
                {
                    "v": PROTOCOL_VERSION,
                    "files": list(argv[1:]),
                    "pid": os.getpid(),
                }
            ),
        )
    except (FileNotFoundError, ConnectionRefusedError, OSError):
        return False
    finally:
        client.close()

    return True


def _allow_foreground(pid: int | None):
    """Let the already-running instance come to the front.

    Windows only grants that to a process the user is working with, which
    is this second instance, and only for a named PID -- not for every
    process on the machine.
    """

    if not env.IS_WINDOWS or not pid:
        return

    import ctypes

    ctypes.windll.user32.AllowSetForegroundWindow(int(pid))


def _peer_pid(client) -> int | None:
    return getattr(client, "peer_pid", None)


def _recv_payload(client) -> bytes:
    header = _recv_exact(client, LENGTH_BYTES)
    if header[0] == PICKLE_PREFIX:
        raise ProtocolError("pickle is not accepted")

    length = int.from_bytes(header, "big")
    if length < 1 or length > MAX_PAYLOAD_BYTES:
        raise ProtocolError("invalid payload length")

    return _recv_exact(client, length)


def _recv_exact(client, n: int) -> bytes:
    return client.recv_exact(n)


def _send_bytes(client, data: bytes) -> None:
    client.send_all(data)


def _connect_client(name: str):
    if env.IS_WINDOWS:
        return _WindowsPipeClient.connect(name)
    return _UnixSocketClient.connect(name)


def _read_pipe_exact(peek, read, n: int, timeout: float) -> bytes:
    """n bytes from a pipe, given up on after timeout seconds of waiting.

    peek() is how many bytes can be read right now (EOFError once the other
    end is gone); read(k) reads k of them, which then cannot block. A
    synchronous Windows pipe read cannot be given a timeout itself, so the
    wait happens here instead.
    """

    deadline = time.monotonic() + timeout
    chunks = bytearray()

    while len(chunks) < n:
        available = peek()

        if available:
            piece = read(min(available, n - len(chunks)))
            if not piece:
                raise EOFError
            chunks.extend(piece)
            continue

        if time.monotonic() >= deadline:
            raise TimeoutError("pipe client sent nothing in time")

        time.sleep(PIPE_POLL_S)

    return bytes(chunks)


class _UnixSocketListener:
    def __init__(self, path: str):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.parent.chmod(0o700)

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._sock.bind(path)
            Path(path).chmod(0o600)
            self._sock.listen(16)
        except OSError:
            self._sock.close()
            raise

    def accept(self):
        conn, _addr = self._sock.accept()
        # a client that never writes is dropped, not waited on for good
        conn.settimeout(CLIENT_READ_TIMEOUT_S)
        return _UnixSocketClient(conn)

    def close(self):
        self._sock.close()
        with contextlib.suppress(OSError):
            self._path.unlink()


class _UnixSocketClient:
    def __init__(self, sock: socket.socket):
        self._sock = sock
        self.peer_pid = None

    @classmethod
    def connect(cls, path: str):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(CLIENT_CONNECT_TIMEOUT_S)
        try:
            sock.connect(path)
        except OSError:
            sock.close()
            raise
        return cls(sock)

    def recv_exact(self, n: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < n:
            piece = self._sock.recv(n - len(chunks))
            if not piece:
                raise EOFError
            chunks.extend(piece)
        return bytes(chunks)

    def send_all(self, data: bytes) -> None:
        self._sock.sendall(data)

    def close(self):
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


if env.IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

    PIPE_ACCESS_DUPLEX = 0x00000003
    FILE_FLAG_FIRST_PIPE_INSTANCE = 0x00080000
    PIPE_TYPE_BYTE = 0x00000000
    PIPE_READMODE_BYTE = 0x00000000
    PIPE_WAIT = 0x00000000
    PIPE_REJECT_REMOTE_CLIENTS = 0x00000008
    PIPE_UNLIMITED_INSTANCES = 255
    ERROR_PIPE_CONNECTED = 535
    ERROR_PIPE_BUSY = 231
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    TOKEN_QUERY = 0x0008
    TokenUser = 1
    ERROR_BROKEN_PIPE = 109

    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("nLength", wintypes.DWORD),
            ("lpSecurityDescriptor", ctypes.c_void_p),
            ("bInheritHandle", wintypes.BOOL),
        ]

    kernel32.CreateNamedPipeW.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(SECURITY_ATTRIBUTES),
    )
    kernel32.CreateNamedPipeW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.ConnectNamedPipe.argtypes = (wintypes.HANDLE, ctypes.c_void_p)
    kernel32.ConnectNamedPipe.restype = wintypes.BOOL
    kernel32.DisconnectNamedPipe.argtypes = (wintypes.HANDLE,)
    kernel32.DisconnectNamedPipe.restype = wintypes.BOOL
    kernel32.WaitNamedPipeW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD)
    kernel32.WaitNamedPipeW.restype = wintypes.BOOL
    kernel32.PeekNamedPipe.argtypes = (
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
    )
    kernel32.PeekNamedPipe.restype = wintypes.BOOL
    kernel32.ReadFile.argtypes = (
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.c_void_p,
    )
    kernel32.ReadFile.restype = wintypes.BOOL
    kernel32.WriteFile.argtypes = (
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.c_void_p,
    )
    kernel32.WriteFile.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.OpenProcessToken.argtypes = (
        wintypes.HANDLE,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.HANDLE),
    )
    kernel32.OpenProcessToken.restype = wintypes.BOOL
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.GetNamedPipeServerProcessId.argtypes = (
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD),
    )
    kernel32.GetNamedPipeServerProcessId.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = (ctypes.c_void_p,)
    kernel32.LocalFree.restype = ctypes.c_void_p
    advapi32.GetTokenInformation.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    )
    advapi32.GetTokenInformation.restype = wintypes.BOOL
    advapi32.ConvertSidToStringSidW.argtypes = (
        ctypes.c_void_p,
        ctypes.POINTER(wintypes.LPWSTR),
    )
    advapi32.ConvertSidToStringSidW.restype = wintypes.BOOL
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(wintypes.ULONG),
    )
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = (
        wintypes.BOOL
    )

    class SID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [
            ("Sid", ctypes.c_void_p),
            ("Attributes", wintypes.DWORD),
        ]

    class TOKEN_USER(ctypes.Structure):
        _fields_ = [("User", SID_AND_ATTRIBUTES)]

    def _current_user_sid() -> str:
        token = wintypes.HANDLE()
        if not kernel32.OpenProcessToken(
            kernel32.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)
        ):
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            size = wintypes.DWORD(0)
            advapi32.GetTokenInformation(token, TokenUser, None, 0, ctypes.byref(size))
            buf = ctypes.create_string_buffer(size.value)
            if not advapi32.GetTokenInformation(
                token, TokenUser, buf, size, ctypes.byref(size)
            ):
                raise ctypes.WinError(ctypes.get_last_error())

            user = TOKEN_USER.from_buffer(buf)
            sid_str = wintypes.LPWSTR()
            if not advapi32.ConvertSidToStringSidW(
                user.User.Sid, ctypes.byref(sid_str)
            ):
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                return sid_str.value
            finally:
                kernel32.LocalFree(sid_str)
        finally:
            kernel32.CloseHandle(token)

    def _user_only_security_attributes():
        """A DACL that grants this user GENERIC_ALL and nobody else."""

        sddl = f"D:P(A;;GA;;;{_current_user_sid()})"
        sd = ctypes.c_void_p()
        sd_size = wintypes.ULONG()
        if not advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            sddl, 1, ctypes.byref(sd), ctypes.byref(sd_size)
        ):
            raise ctypes.WinError(ctypes.get_last_error())

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
        sa.lpSecurityDescriptor = sd
        sa.bInheritHandle = False
        return sa, sd

    def _pipe_open_mode() -> int:
        return PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE

    def _pipe_mode() -> int:
        return (
            PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS
        )

    class _WindowsPipeListener:
        def __init__(self, name: str):
            self._name = name
            self._closed = threading.Event()
            self._sa, self._sd = _user_only_security_attributes()
            self._handle = self._create_pipe(first=True)
            self.pipe_mode = _pipe_mode()

        def _create_pipe(self, first: bool):
            open_mode = PIPE_ACCESS_DUPLEX
            if first:
                open_mode |= FILE_FLAG_FIRST_PIPE_INSTANCE

            handle = kernel32.CreateNamedPipeW(
                self._name,
                open_mode,
                _pipe_mode(),
                PIPE_UNLIMITED_INSTANCES,
                MAX_PAYLOAD_BYTES + LENGTH_BYTES,
                MAX_PAYLOAD_BYTES + LENGTH_BYTES,
                0,
                ctypes.byref(self._sa),
            )
            if handle == INVALID_HANDLE_VALUE:
                raise ctypes.WinError(ctypes.get_last_error())
            return handle

        def accept(self):
            while not self._closed.is_set():
                connected = kernel32.ConnectNamedPipe(self._handle, None)
                err = ctypes.get_last_error()
                if connected or err == ERROR_PIPE_CONNECTED:
                    handle = self._handle
                    try:
                        self._handle = self._create_pipe(first=False)
                    except OSError:
                        self._handle = handle
                        raise
                    return _WindowsPipeClient(handle)

                kernel32.DisconnectNamedPipe(self._handle)

            raise OSError("listener closed")

        def close(self):
            self._closed.set()
            handle = self._handle
            self._handle = None
            if handle:
                kernel32.CloseHandle(handle)
            if self._sd:
                kernel32.LocalFree(self._sd)
                self._sd = None

    class _WindowsPipeClient:
        def __init__(self, handle, peer_pid: int | None = None):
            self._handle = handle
            self.peer_pid = peer_pid

        @classmethod
        def connect(cls, name: str):
            handle = kernel32.CreateFileW(
                name,
                GENERIC_READ | GENERIC_WRITE,
                0,
                None,
                OPEN_EXISTING,
                0,
                None,
            )
            if handle == INVALID_HANDLE_VALUE:
                err = ctypes.get_last_error()
                if err == ERROR_PIPE_BUSY:
                    wait_ms = int(CLIENT_CONNECT_TIMEOUT_S * 1000)
                    if not kernel32.WaitNamedPipeW(name, wait_ms):
                        raise ctypes.WinError(ctypes.get_last_error())
                    handle = kernel32.CreateFileW(
                        name,
                        GENERIC_READ | GENERIC_WRITE,
                        0,
                        None,
                        OPEN_EXISTING,
                        0,
                        None,
                    )
                if handle == INVALID_HANDLE_VALUE:
                    raise ctypes.WinError(ctypes.get_last_error())

            pid = wintypes.DWORD(0)
            peer_pid = None
            if kernel32.GetNamedPipeServerProcessId(handle, ctypes.byref(pid)):
                peer_pid = pid.value

            return cls(handle, peer_pid=peer_pid)

        def recv_exact(self, n: int) -> bytes:
            return _read_pipe_exact(self._peek, self._read, n, CLIENT_READ_TIMEOUT_S)

        def _peek(self) -> int:
            available = wintypes.DWORD(0)
            if not kernel32.PeekNamedPipe(
                self._handle, None, 0, None, ctypes.byref(available), None
            ):
                err = ctypes.get_last_error()
                if err == ERROR_BROKEN_PIPE:
                    raise EOFError
                raise ctypes.WinError(err)
            return available.value

        def _read(self, k: int) -> bytes:
            buf = ctypes.create_string_buffer(k)
            read = wintypes.DWORD(0)
            if not kernel32.ReadFile(self._handle, buf, k, ctypes.byref(read), None):
                raise ctypes.WinError(ctypes.get_last_error())
            return buf.raw[: read.value]

        def send_all(self, data: bytes) -> None:
            offset = 0
            while offset < len(data):
                written = wintypes.DWORD(0)
                remaining = len(data) - offset
                chunk = data[offset : offset + remaining]
                buf = (ctypes.c_char * remaining).from_buffer_copy(chunk)
                if not kernel32.WriteFile(
                    self._handle, buf, remaining, ctypes.byref(written), None
                ):
                    raise ctypes.WinError(ctypes.get_last_error())
                if written.value == 0:
                    raise OSError("pipe write returned zero")
                offset += written.value

        def close(self):
            if self._handle:
                kernel32.CloseHandle(self._handle)
                self._handle = None

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.close()
