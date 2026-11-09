# Platforms

GridPlayer Alabaster supports **Windows 10 and 11, 64-bit**, only.

| Platform | Status |
| --- | --- |
| Windows 10/11 (64-bit) | Supported. Developed and tested here. |
| Linux | Not supported. No packages from this project. |
| macOS | Not supported. No packages from this project. |

The source still contains upstream GridPlayer's macOS and Linux code and the
upstream build recipes in `scripts/` and the `justfile`
(`build-linux-appimage`, `build-linux-snap`, `build-linux-flatpak`,
`build-macos-package`). This project does not run, test or fix them. Anyone
may port Alabaster from the source under the GPL. The `gridplayer` packages on
Flathub, the Snap Store, PyPI and the upstream DMG are upstream GridPlayer, not
Alabaster.

## Windows packages

The portable zip is out as release candidate [v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1), a
prerelease. Other packages will appear on the
[Releases page](https://github.com/XDevMatt/alabaster-gridplayer/releases).

| Package | Status |
| --- | --- |
| Portable zip, `GridPlayer-Alabaster-<commit>-win64-portable.zip` | Release candidate: [v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1) (prerelease, unsigned). |
| Installer, `GridPlayer-<version>-win64-install.exe` | Can be built. Not released yet. |
| Chocolatey `gridplayer-alabaster` | Draft in `packaging/chocolatey`. Needs a published installer and its checksum. |
| From source | Works. See [Building from source](building.md). |

## What's bundled

The Windows build includes its own copy of VLC (libVLC 3.0.24), so VLC does
not have to be installed, plus the yt-dlp and Streamlink Python modules.

No build bundles command-line tools: ffmpeg, ffprobe, the yt-dlp program and
Deno. Install and update them yourself:
`winget install Gyan.FFmpeg`, `winget install yt-dlp.yt-dlp`,
`winget install DenoLand.Deno`, or `choco install deno ffmpeg yt-dlp -y`.
See [Requirements](quick-start.md#requirements).
