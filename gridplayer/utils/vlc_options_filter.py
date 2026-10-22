"""Deny-list for misc/vlc_options so this box cannot open a listener."""

# flags that start a server, stream-out, or turn Lua back on
_BLOCKED_NAMES = frozenset(
    {
        "--http-port",
        "--https-port",
        "--rtsp-port",
        "--telnet-port",
        "--http-host",
        "--https-host",
        "--rtsp-host",
        "--telnet-host",
        "--rc-host",
        "--rc-port",
        "--extraintf",
        "--control",
        "--sout",
        "--sout-keep",
        "--sout-all",
        "--lua",
        "--lua-intf",
        "--lua-config",
        "--http-src",
        "--http-password",
        "--telnet-password",
    }
)

_BLOCKED_PREFIXES = (
    "--http-port",
    "--https-port",
    "--rtsp-port",
    "--telnet-port",
    "--extraintf",
    "--control",
    "--sout",
    "--lua",
    "--rc-",
    "--satip",
    "--srt-",
)

_BLOCKED_INTF = frozenset({"http", "https", "telnet", "rc", "lua", "luarc", "luahttp"})


def filter_vlc_options(options: list[str]) -> list[str]:
    """Drop listener / stream-out / Lua flags. Keep decoder and filter flags."""

    kept = []
    for opt in options:
        if _is_blocked(opt):
            continue
        kept.append(opt)
    return kept


def with_no_lua_last(options: list[str]) -> list[str]:
    """Ensure --no-lua wins over anything typed by hand."""

    return [opt for opt in options if opt != "--no-lua"] + ["--no-lua"]


def _is_blocked(opt: str) -> bool:
    body = opt.strip()
    if not body.startswith("-"):
        return False

    name, _, value = body.partition("=")
    name_l = name.lower()
    value_l = value.lower()

    if name_l in _BLOCKED_NAMES:
        return True

    if any(
        name_l == prefix or name_l.startswith(prefix) for prefix in _BLOCKED_PREFIXES
    ):
        return True

    if name_l in {"--intf", "--extraintf", "--control"}:
        parts = {part.strip() for part in value_l.replace(":", ",").split(",") if part}
        if parts & _BLOCKED_INTF:
            return True

    return False
