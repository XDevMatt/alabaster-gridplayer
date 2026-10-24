"""What the dubbed-stream scenarios share: dubs (HLS) and dubs_dash."""

from gridplayer.utils.track_language import normalize

SETTINGS = {
    # Streamlink takes only the default audio of an HLS stream; yt-dlp
    # reads each rendition and its language
    "streaming/resolver_priority": "yt_dlp",
}

NAMES = {"en": "English", "es": "Spanish"}


def dubbed(d, path: str, what: str):
    """The checks for one dubbed stream, at this path under the dubs folder."""

    d.open(f"{d.serve(d.media.dubs)}/{path}")
    dubs = d.wait_for_cell(path.rsplit("/", 1)[-1])

    d.check(
        "both languages",
        set(dubs.stream.audio_language_options) == {"en", "es"},
        dubs.stream.audio_language_options,
    )
    d.check(
        f"handed to VLC as the {what}",
        dubs.stream._is_whole_manifest_playing,
    )
    d.wait_until(lambda: _heard(dubs) in NAMES, "VLC plays one of the languages")
    playing = dubs.stream.audio_language_playing
    d.check("the language said is the one heard", playing == _heard(dubs), playing)
    other = "en" if playing == "es" else "es"
    d.menu(dubs, "menu_generator_audio_track")

    loaded_at = dubs.stream._loaded_at
    d.choose(dubs, "menu_generator_audio_track", NAMES[other])
    d.wait_until(
        lambda: _heard(dubs) == other and dubs.is_playable,
        f"VLC plays the {NAMES[other]} track",
    )
    d.check("said as playing", dubs.stream.audio_language_playing == other)
    d.check("switched without a reload", dubs.stream._loaded_at == loaded_at)

    d.choose(dubs, "menu_generator_stream_quality", "180p")
    d.wait_until(
        lambda: dubs.stream.quality_playing.startswith("180p") and dubs.is_playable,
        "180p plays",
    )
    d.wait_until(lambda: _heard(dubs) == other, "still heard in the language chosen")
    d.check(
        "in the language chosen",
        dubs.stream.audio_language_playing == other,
        dubs.stream.audio_language_playing,
    )

    d.note("end", dubs)


def _heard(block):
    """The language of the track VLC is playing, as VLC says it."""

    track = (block.audio.tracks or {}).get(block.audio.track_playing)

    if track is None or not track.language:
        return None

    heard = normalize(track.language)

    return next((tag for tag in NAMES if normalize(tag) == heard), heard)
