import os
import re
import signal
from contextlib import suppress
from multiprocessing.process import active_children

from gridplayer.params import env


def force_terminate_resource_tracker():
    # windows doesn't have resource tracker
    if env.IS_WINDOWS:
        return

    # kill resource_tracker first so it won't complain about leaked resources
    from multiprocessing.resource_tracker import _resource_tracker

    if _resource_tracker._pid is not None:
        os.kill(_resource_tracker._pid, signal.SIGKILL)


def force_terminate_children():
    for p in active_children():
        # the process manager closes the ones that exit as they do
        with suppress(ValueError):
            p.terminate()


def force_terminate_children_all():
    force_terminate_resource_tracker()
    force_terminate_children()


def force_terminate(exit_code: int = 0):
    with suppress(ValueError):
        force_terminate_children_all()
    os._exit(exit_code)


def is_url(s) -> bool:
    return bool(re.match("^[a-z]+://", s))


# what a share on this computer itself is reached by: \\?\C:\ and
# \\.\ are not shares at all
_LOCAL_HOSTS = frozenset(("?", ".", "localhost", "127.0.0.1", "::1"))


def is_remote_share(uri: str) -> bool:
    """A path on another computer, \\\\host\\share or //host/share. Only
    looking at one has Windows log in to that host as the viewer, sending
    their password's hash to whoever runs it; a drive letter mapped to a
    share is not one of these, and is looked at as ever."""

    path = uri.replace("/", "\\")

    if not path.startswith("\\\\"):
        return False

    host, _, rest = path[2:].partition("\\")
    host = host.lower()

    # \\?\UNC\host\share is a share all the same
    if host == "?" and rest.lower().startswith("unc\\"):
        return True

    return host not in _LOCAL_HOSTS
