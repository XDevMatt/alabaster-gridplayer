"""A startup-option complaint is never told as why a video failed."""

import threading

from gridplayer.vlc_player import vlc_errors


def test_unknown_startup_option_is_not_kept():
    vlc_errors.keep_vlc_error("main: option quiet does not exist")
    vlc_errors.keep_vlc_error("main: option quiet does not exist")
    vlc_errors.keep_vlc_error("avcodec: cannot start decoder")

    said = vlc_errors.vlc_errors_since(0, {threading.get_ident()})

    assert "avcodec: cannot start decoder" in said
    assert not any("does not exist" in line for line in said)


def test_no_instance_is_given_quiet():
    """libVLC 3 has no --quiet (only --quiet-synchro) and says so."""

    import pathlib

    root = pathlib.Path(vlc_errors.__file__).resolve().parents[1]
    for name in ("vlc_player/instance.py", "utils/media_shape.py", "utils/item_info.py"):
        assert '"--quiet"' not in (root / name).read_text(encoding="utf-8")
