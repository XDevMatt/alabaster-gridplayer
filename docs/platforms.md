# Platforms

GridPlayer Alabaster is built on the GridPlayer framework by vzhd1701 and
maintained by XDevMatt. All platforms build from one codebase. There is no
separate fork for any system.

| Platform | Status |
| --- | --- |
| Windows 10/11 | Primary. Developed and tested here first. |
| Linux | Second. Supported, but tested less. |
| macOS | Community-maintained and untested. |

No Alabaster release has been published yet. Releases will appear on the
[Releases page](https://github.com/XDevMatt/gridplayer-alabaster/releases),
Windows builds first.

## Windows

Windows 10 and 11 are the main target and get the most testing.

- **Portable zip**: the first download to be published, named
  `GridPlayer-<version>-win64-portable.zip`. Extract it and run
  `GridPlayer.exe`. See [Quick start](quick-start.md).
- **Installer**: the build can make one
  (`GridPlayer-<version>-win64-install.exe`), but none is published yet.

## Linux

Linux is supported and builds from the same code, but gets less testing than
Windows.

There is no Alabaster package for Linux yet. Run it from source (see
[Building from source](building.md)), or use a build someone in the community
makes. The `justfile` still has the upstream recipes for an AppImage, a Snap
and a Flatpak (`build-linux-appimage`, `build-linux-snap`,
`build-linux-flatpak`).

The `gridplayer` packages on Flathub, the Snap Store and PyPI are upstream
GridPlayer, not Alabaster. Alabaster keeps its settings in a folder of its
own, so the two don't share settings.

## macOS

macOS builds come from the same codebase as Windows and Linux. The macOS
version is community-maintained, and XDevMatt doesn't test it.

What comes from upstream GridPlayer:

- Upstream ships a macOS arm64 (Apple Silicon) DMG.
- Upstream CI has `macos-15` and `macos-15-intel` jobs, and the macOS build job
  runs before releases.

Alabaster doesn't publish a macOS DMG. The `justfile` recipes
`build-macos-package-arm64` and `build-macos-package` can make one, but that
build is untested. Mac users build from source or use a community build.

## What's bundled

The Windows build includes its own copy of VLC (libVLC 3.0.24), the
playback engine, so VLC doesn't have to be installed, and the yt-dlp and
Streamlink Python modules.

No build bundles command-line tools: ffmpeg, ffprobe, the yt-dlp program and
Deno. They change often, so you install and update them yourself:
`winget install Gyan.FFmpeg`, `winget install yt-dlp.yt-dlp` and
`winget install DenoLand.Deno` on Windows, `brew install ffmpeg yt-dlp deno`
on macOS, your package manager on Linux. See
[Requirements](quick-start.md#requirements) for what each one is for and
how to point Alabaster at a yt-dlp of your own.

## Build scripts

The upstream GridPlayer build scripts for all three platforms are still in
`scripts/` and the `justfile`. See [Building from source](building.md).
