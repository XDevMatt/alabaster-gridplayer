# ruff: noqa: RUF001
"""A saved SubtitleCat file is one libVLC can read as UTF-8 from end to end.

libVLC reads a text subtitle as UTF-8 only until the first invalid cue, then
drops later cues it cannot convert from the fallback character set. These
check what lands on disk, not how it got there.
"""

from gridplayer.plugins.subtitlecat.save import save_bytes


def _srt(*cues: str) -> str:
    return "".join(
        f"{n}\r\n00:00:0{n},000 --> 00:00:0{n},900\r\n{text}\r\n\r\n"
        for n, text in enumerate(cues, start=1)
    )


GREEK = _srt("Ζούμε σε έναν υπολογιστή", "όταν αλλάζουν οι μεταβλητές", "Νέο")


def test_a_valid_utf8_file_is_saved_byte_for_byte(tmp_path):
    body = GREEK.encode("utf-8")

    path = save_bytes(tmp_path, "a.srt", body)

    assert path.read_bytes() == body


def test_one_stray_byte_no_longer_blanks_the_rest_of_the_file(tmp_path):
    good = GREEK.encode("utf-8")
    first_text = good.index(b"\r\n", good.index(b"-->")) + 2
    body = good[:first_text] + b"\x93" + good[first_text:]

    saved = save_bytes(tmp_path, "a.srt", body).read_bytes().decode("utf-8")

    assert saved == GREEK.replace("Ζούμε", "\u201cΖούμε", 1)


def test_stray_windows_1252_quotes_in_english_are_kept_as_quotes(tmp_path):
    body = (
        _srt("She said \u201chi\u201d", "Bye")
        .encode("utf-8")
        .replace("\u201chi\u201d".encode("utf-8"), b"\x93hi\x94")
    )
    body = body + _srt("Caf\u00e9", "na\u00efve", "fa\u00e7ade").encode("utf-8")

    saved = save_bytes(tmp_path, "a.srt", body).read_bytes().decode("utf-8")

    assert "She said \u201chi\u201d" in saved
    assert "fa\u00e7ade" in saved


def test_a_byte_windows_1252_lacks_becomes_a_replacement_character(tmp_path):
    body = _srt("Caf\u00e9 cr\u00e8me", "x").encode("utf-8") + b"\x81"

    saved = save_bytes(tmp_path, "a.srt", body).read_bytes()

    assert saved.decode("utf-8").endswith("\ufffd")


def test_a_legacy_file_is_left_for_the_encoding_setting(tmp_path):
    for codec, text in (
        ("cp1251", "Привет мир, как дела"),
        ("cp1252", "Caf\u00e9 cr\u00e8me br\u00fbl\u00e9e"),
    ):
        body = _srt(text, text).encode(codec)

        path = save_bytes(tmp_path, f"{codec}.srt", body)

        assert path.read_bytes() == body


def test_utf16_with_a_byte_order_mark_is_left_alone(tmp_path):
    body = GREEK.encode("utf-16")

    path = save_bytes(tmp_path, "a.srt", body)

    assert path.read_bytes() == body


def test_a_byte_order_mark_survives_a_repair(tmp_path):
    body = b"\xef\xbb\xbf" + GREEK.encode("utf-8") + b"\x93"

    saved = save_bytes(tmp_path, "a.srt", body).read_bytes()

    assert saved.startswith(b"\xef\xbb\xbf")
    saved.decode("utf-8")
