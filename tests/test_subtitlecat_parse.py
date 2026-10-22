"""Parsers against saved SubtitleCat pages. No network."""

from pathlib import Path

from gridplayer.plugins.subtitlecat.parse import (
    _language_rank,
    is_subtitle_payload,
    message_from_response,
    order_languages,
    parse_detail,
    parse_search,
    preferred_language_codes,
    srt_url_from_json,
    visible_text,
)

FIXTURES = Path(__file__).parent / "fixtures" / "subtitlecat"
VIP = (
    "You are out of free translations. You can either wait one hour, "
    "or sign up to a VIP account for unlimited translations!"
)


def _text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_search_reads_sintel_and_skips_load_more():
    hits = parse_search(_text("search-sintel.html"))

    assert [hit.title for hit in hits] == [
        "Sintel (2010)",
        "classicalhd-sintel.2010.en-1080p",
        "Sintel.2010.720p",
    ]
    assert hits[0].href == (
        "https://www.subtitlecat.com/subs/751/Sintel%20%282010%29.eng.html"
    )
    assert hits[0].size == "2 KB"
    assert hits[0].downloads == "19"
    assert hits[0].languages == "19"
    assert hits[0].source_language == "English"
    assert hits[2].source_language == "Romanian"
    assert all("example.com" not in hit.href for hit in hits)
    assert all("show=1000" not in hit.href for hit in hits)


def test_a_subtitle_page_lists_downloads_and_a_translate_button():
    rows = {row.code: row for row in parse_detail(_text("page-sintel.html"))}

    assert rows["en"].name == "English"
    assert rows["en"].download_url.endswith("/subs/751/Sintel%20%282010%29.eng-en.srt")
    assert "/subs/1158/" in rows["es"].download_url
    assert rows["es-419"].code == "es-419"
    assert rows["zh-TW"].download_url.endswith("eng-zh-TW.srt")
    assert rows["sq"].download_url is None
    assert rows["sq"].translate.language == "sq"
    assert rows["sq"].translate.filename == "Sintel (2010).eng-orig.srt"
    assert rows["sq"].translate.folder == "/subs/751/"
    assert rows["fr"].download_url is None
    assert all(
        row.download_url is None or "example.com" not in row.download_url
        for row in rows.values()
    )


def test_a_limit_page_keeps_subtitlecats_sentence_and_drops_scripts():
    html = _text("limit-message.html")

    assert visible_text(html) == VIP
    assert "secret-cookie" not in visible_text(html)
    assert (
        message_from_response("text/html; charset=utf-8", html.encode("utf-8")) == VIP
    )


def test_json_is_not_rewritten_and_an_srt_url_can_be_offered():
    raw = '{"ok": true, "file": "https://www.subtitlecat.com/subs/751/A.srt"}'

    assert message_from_response("application/json", raw.encode()) == raw
    assert srt_url_from_json(raw) == "https://www.subtitlecat.com/subs/751/A.srt"
    assert srt_url_from_json('{"file": "https://example.com/A.srt"}') is None


def test_preferred_languages_and_a_regional_code():
    rows = parse_detail(_text("page-sintel.html"))

    english_first = [row.code for row in order_languages(rows, ["en"])]
    assert english_first[0] == "en"

    traditional = [row.code for row in order_languages(rows, ["zh-TW"])]
    assert traditional[0] == "zh-TW"
    assert _language_rank("zh-CN", ["zh-TW"])[0] == 2
    assert _language_rank("zh-TW", ["zh"])[0] == 1
    assert _language_rank("en-GB", ["en"]) == (1, 0)
    assert _language_rank("en", ["en"]) == (0, 0)

    assert preferred_language_codes("en, ja", "fr_FR") == ("en", "ja")
    assert preferred_language_codes("", "en_US") == ("en",)
    assert preferred_language_codes("zh_TW", "") == ("zh-TW",)


def test_subtitle_bytes_are_told_from_html():
    cue = b"1\n00:00:00,000 --> 00:00:01,000\nHi\n"

    assert is_subtitle_payload("text/plain", cue)
    assert is_subtitle_payload("application/octet-stream", b"WEBVTT\n")
    assert not is_subtitle_payload("text/html", cue)
    assert not is_subtitle_payload("text/plain", b"<!DOCTYPE html><html></html>")
