"""File names drop apostrophes and cannot leave their folder."""

from gridplayer.plugins.subtitlecat.names import (
    _APOSTROPHES,
    name_from_url,
    safe_subtitle_name,
    search_terms,
)


def test_search_terms_join_letters_around_an_apostrophe():
    assert search_terms("Britain's Got Talent.mkv") == "Britains Got Talent"


def test_search_terms_treat_dots_and_underscores_as_spaces():
    assert search_terms("Sintel.2010.720p_BluRay.mkv") == "Sintel 2010 720p BluRay"


def test_every_apostrophe_mark_is_dropped():
    for mark in _APOSTROPHES:
        assert safe_subtitle_name(f"Britain{mark}s.srt") == "Britains.srt"
        assert search_terms(f"Britain{mark}s Got Talent.mkv") == "Britains Got Talent"


def test_a_saved_name_keeps_parentheses_and_decodes_the_url():
    assert (
        name_from_url(
            "https://www.subtitlecat.com/subs/751/Sintel%20%282010%29.eng-en.srt"
        )
        == "Sintel (2010).eng-en.srt"
    )


def test_path_characters_cannot_leave_the_folder():
    raw = "..\\..\\Britain's:Got|Talent?.srt"
    assert safe_subtitle_name(raw) == "BritainsGotTalent.srt"
    assert "/" not in safe_subtitle_name("a/b/c.srt")
    assert safe_subtitle_name("a/b/c.srt") == "c.srt"


def test_controls_and_quotes_are_removed():
    assert safe_subtitle_name('A\x00B<C>D"E.srt') == "ABCDE.srt"


def test_a_device_name_is_not_used():
    assert safe_subtitle_name("con.srt") == "subtitle.srt"
    assert safe_subtitle_name("..") == "subtitle.srt"
    assert safe_subtitle_name("") == "subtitle.srt"


def test_an_extension_is_added_when_the_url_has_none():
    assert safe_subtitle_name("Britains") == "Britains.srt"


def test_percent_encoded_slashes_stay_in_the_last_segment():
    # Split first, then decode, so %2F cannot become a directory.
    assert safe_subtitle_name("subs/1/a%2F..%2Fb.srt") == "a..b.srt"
