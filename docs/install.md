# Install on Windows

GridPlayer Alabaster is a Windows app. There are a few ways it's meant to be
installed. The **portable ZIP** is out as release candidate
[v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1), a prerelease. The installer and the packages below are
not released yet. You can also [run it from source](building.md).

| Way | What you get | Status |
| --- | --- | --- |
| **Installer** (`.exe`) | Start menu entry, optional desktop icon, file associations, an uninstall entry | Not released yet |
| **Portable ZIP** | A folder you unzip anywhere; settings stay inside it | [v0.2beta_rc1 prerelease](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1) |
| **Chocolatey** (`alabaster-gridplayer`) | The installer, plus ffmpeg, yt-dlp and Deno pulled in for you | Planned, not submitted |
| **PortableApps.com** | A `.paf.exe` for the PortableApps.com Platform | Planned, not submitted |

!!! warning "Not on PyPI, not on Scoop"
    Alabaster is not published on PyPI. `pip install gridplayer` and
    `uv tool install gridplayer` install **upstream** GridPlayer. The
    `gridplayer` packages on Chocolatey, Scoop, Flathub and the Snap Store are
    upstream GridPlayer too. There's no Scoop package for Alabaster.

## Installer

The installer is not released yet. When it is, download `GridPlayer-<version>-win64-install.exe`
and run it. It installs to `C:\Program Files\GridPlayer Alabaster\` by default
(64-bit Windows only), next to any upstream GridPlayer install, adds a Start menu entry, can add a desktop icon, and
registers Alabaster for common media file types so they show up under
**Open with**.
Uninstall it from Windows Settings, Apps.

Settings live in `C:\Users\<user>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster\`.
See [Data folder and portable mode](reference/data-folder.md).

## Portable ZIP

Download `GridPlayer-Alabaster-57f21b1-win64-portable.zip` from the
[v0.2beta_rc1 prerelease page](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1). It is a release candidate for Windows
10 and 11 (64-bit). The build is not code-signed, so Windows SmartScreen may
warn before it runs. Size 135,235,014 bytes; SHA256
`02af3a7c5b5508598978efa9f950e250f2d0ed7f378032f17e079078793ed745`.

1. Unzip it to a new folder you own, for example `C:\Tools\`. The ZIP holds
   one folder, `GridPlayer-Alabaster-portable`. Don't unzip it over an
   installed upstream GridPlayer; it doesn't touch one.
2. Run `GridPlayer.exe` inside `GridPlayer-Alabaster-portable`.

The ZIP has a `portable_data` folder next to `GridPlayer.exe`. While
that folder is there, settings, logs, cache and screenshots go into it, and
nothing is written to `AppData`. Delete `portable_data` and the app uses the
normal settings folder instead.

## Chocolatey (planned)

The package id will be **`alabaster-gridplayer`**. It isn't on the Chocolatey
community repository yet. Once it is:

```powershell
choco install alabaster-gridplayer -y
```

It will install the Alabaster installer silently and pull in three helper
packages: `ffmpeg` (which brings `ffprobe` with it), `yt-dlp` and `deno`.
Never install the package named `gridplayer`: that's upstream GridPlayer.

## PortableApps.com (planned)

A PortableApps.com package is on the
[roadmap](roadmap.md#portableappscom-package). The standalone portable zip is
not in their format. The plan is to wrap it as a `.paf.exe`, host that file
publicly, and post a development test on their beta testing forum. They do
not take uploads, and a forum post is not an automatic store listing.

## What's in the box, and what isn't

The Windows build carries its own copy of VLC (libVLC 3.0.24), so **you don't
need VLC installed**. It also carries the Python runtime, PyQt5, and the
yt-dlp and Streamlink Python modules it resolves links with.

These are **not** bundled in current builds:

| Tool | What it's for | Do you need it? |
| --- | --- | --- |
| **Deno** | Lets yt-dlp solve YouTube's JavaScript challenge | Only if YouTube links fail to play |
| **yt-dlp.exe** (the program) | A yt-dlp you keep updated yourself, used instead of the built-in module | Optional |
| **ffmpeg / ffprobe** | Reserved for merging streams whose sound comes separately in ways VLC can't pair (YouTube DASH files, for example) | No current feature runs them yet |

Local files, folders, playlists and most links play without any of them.

### Installing the helpers yourself

With Chocolatey:

```powershell
choco install ffmpeg yt-dlp deno -y
choco upgrade ffmpeg yt-dlp deno -y
```

Or with winget:

```powershell
winget install Gyan.FFmpeg
winget install yt-dlp.yt-dlp
winget install DenoLand.Deno
```

Then restart Alabaster. Keep them updated: sites change often and an old
yt-dlp or Deno stops working.

### Pointing Alabaster at them

- **Deno**: Settings, Streaming, Link Resolution, **JavaScript runtime**: a
  folder that has `deno.exe`. Empty means `deno` on your `PATH`.
- **yt-dlp**: Settings, Streaming, Link Resolution, **External yt-dlp**: the
  full path to `yt-dlp.exe`, or just `yt-dlp` to use the one on `PATH`.
  Empty, or not found, means the built-in yt-dlp module. Installing yt-dlp
  with Chocolatey or winget does nothing until you set this.
- **Test a YouTube link** on the same page shows which JavaScript engine
  will be used and where it is.

If you started Alabaster from a shortcut before installing a helper, the
shortcut may still have the old `PATH`. Sign out and back in, or set the
folder in Settings.

## Side by side with upstream GridPlayer

Alabaster uses its own settings folder (`GridPlayer-Alabaster`) and its own
single-instance channel, so an installed upstream GridPlayer keeps its
settings and keeps receiving its own "Open with" files. The installer
itself still needs its own Windows id and folder before it's published; see
[FAQ](faq.md#can-i-keep-upstream-gridplayer-installed).

## Other systems

Windows is the only target. Mac, Linux, Snap, Flatpak and translations into
other languages aren't project goals. The source is GPLv3, so anyone is
welcome to port it. See [Platforms](platforms.md).
