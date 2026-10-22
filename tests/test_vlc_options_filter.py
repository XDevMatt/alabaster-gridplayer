from gridplayer.utils.vlc_options_filter import filter_vlc_options, with_no_lua_last


def test_decoder_flags_are_kept():
    assert filter_vlc_options(["--avcodec-hw=any", "--freetype-color=0x00ff00"]) == [
        "--avcodec-hw=any",
        "--freetype-color=0x00ff00",
    ]


def test_listener_flags_are_dropped():
    dropped = filter_vlc_options(
        [
            "--http-port=8080",
            "--extraintf=http",
            "--sout=#http{dst=:8080}",
            "--telnet-port=4212",
            "--control=rc",
            "--intf=http",
            "--lua",
            "--avcodec-hw=any",
        ]
    )

    assert dropped == ["--avcodec-hw=any"]


def test_no_lua_is_forced_last():
    assert with_no_lua_last(["--no-lua", "--lua", "--quiet"])[-1] == "--no-lua"
    assert with_no_lua_last(["--quiet"])[-1] == "--no-lua"
