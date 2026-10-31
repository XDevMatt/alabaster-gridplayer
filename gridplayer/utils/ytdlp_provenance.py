"""Which yt-dlp resolves links: an owner-chosen program, or the module.

Lookup order:

1. streaming/ytdlp_external_path, when set. A path to a file is run as
   is. A bare name such as ``yt-dlp`` is looked up on PATH, which is how
   the owner says "the one I installed and keep updated" (winget, brew,
   pip --user...).
2. Otherwise the yt_dlp Python module the app ships with, run in process.

PATH is not searched when the setting is empty: the module is always
there and is what every other part of the app (byte source, checkups,
web lists) talks to, so silently swapping engines because some yt-dlp
happens to be on PATH would make behaviour depend on the machine.
"""

import json
import shutil
import subprocess
from pathlib import Path

from gridplayer.settings import Settings

# a resolve that hangs this long has failed
EXTERNAL_TIMEOUT_S = 120


def bundled_module_name() -> str:
    return "yt_dlp"


def configured_value() -> str:
    try:
        raw = Settings().get("streaming/ytdlp_external_path")
    except (KeyError, ValueError):
        return ""

    return str(raw or "").strip()


def external_binary(configured: str | None = None) -> Path | None:
    """The yt-dlp program to run, or None to use the bundled module."""

    value = configured_value() if configured is None else configured.strip()

    if not value:
        return None

    path = Path(value).expanduser()
    if path.is_file():
        return path

    # a bare name means "the one on PATH"
    if path.name == value:
        found = shutil.which(value)
        if found:
            return Path(found)

    return None


class ExternalYtdlpError(Exception):
    """The external yt-dlp failed; the message is its stderr."""


def cli_args(opts: dict) -> list[str]:
    """Command-line flags for the YoutubeDL options GridPlayer sets."""

    args = []

    if opts.get("noplaylist"):
        args.append("--no-playlist")
    if opts.get("extract_flat") == "in_playlist":
        args.append("--flat-playlist")
    if opts.get("playlistend"):
        args += ["--playlist-end", str(opts["playlistend"])]
    if "proxy" in opts:
        args += ["--proxy", opts["proxy"] or ""]
    for key, value in (opts.get("http_headers") or {}).items():
        args += ["--add-header", f"{key}:{value}"]
    if opts.get("source_address"):
        args += ["--source-address", opts["source_address"]]
    if opts.get("nocheckcertificate"):
        args.append("--no-check-certificates")
    if opts.get("socket_timeout"):
        args += ["--socket-timeout", str(opts["socket_timeout"])]

    browser = opts.get("cookiesfrombrowser")
    if browser:
        name, profile = browser[0], browser[1]
        args += ["--cookies-from-browser", f"{name}:{profile}" if profile else name]

    for name, config in (opts.get("js_runtimes") or {}).items():
        path = (config or {}).get("path")
        args += ["--js-runtimes", f"{name}:{path}" if path else name]

    return args


class ExternalYtdlp:
    """Stands in for a YoutubeDL where only extract_info is needed."""

    def __init__(self, binary: Path, opts: dict):
        self.binary = binary
        self.opts = opts

    def extract_info(self, url: str, download: bool = False, ie_key=None) -> dict:
        command = [str(self.binary), "-J", "--no-warnings", *cli_args(self.opts)]
        if ie_key:
            command += ["--use-extractors", ie_key]
        command += ["--", url]

        try:
            done = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=EXTERNAL_TIMEOUT_S,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ExternalYtdlpError(str(e)) from e

        if done.returncode != 0:
            raise ExternalYtdlpError(done.stderr.strip() or f"exit {done.returncode}")

        try:
            return json.loads(done.stdout)
        except ValueError as e:
            raise ExternalYtdlpError("yt-dlp printed no JSON") from e
