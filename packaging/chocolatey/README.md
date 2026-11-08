# Chocolatey package: gridplayer-alabaster (maintainer notes)

Draft package. Nothing has been packed, pushed or submitted, and no
GridPlayer Alabaster package or installer has been published.

## Identity

- Package id: **`gridplayer-alabaster`**. Never `gridplayer`,
  `gridplayer.install` or `gridplayer.portable`: those belong to upstream
  GridPlayer (`gridplayer` is live on the community repository at 0.5.5).
- On 2026-11-08 `https://community.chocolatey.org/packages/gridplayer-alabaster`
  returned 404, so the id isn't taken. Ownership is set by the first
  approved push.
- Project URL: `https://github.com/XDevMatt/alabaster-gridplayer`.
- One package only: it wraps the Inno Setup installer. No separate portable
  or meta packages.

## Dependencies

Add to the nuspec `<metadata>`:

```xml
<dependencies>
  <dependency id="ffmpeg" version="[9.0.2,)" />
  <dependency id="yt-dlp" version="[2026.10.26,)" />
  <dependency id="deno" version="[2.9.8,)" />
</dependencies>
```

The minimums are the newest **stable** versions seen on 2026-11-08. Replace
them with the versions actually tested on a clean machine before packing.
No VLC dependency: libVLC is bundled in the app.

| Package | Seen 2026-11-08 | Notes |
| --- | --- | --- |
| [`ffmpeg`](https://community.chocolatey.org/packages/ffmpeg) | 9.0.2, approved 2026-09-20, no dependencies | Ships **ffprobe** too (see below). |
| [`yt-dlp`](https://community.chocolatey.org/packages/yt-dlp) | Stable 2026.10.26; the page header shows a nightly prerelease (2026.11.4.232659-nightly) | Plain `choco install` takes the stable; nightlies need `--pre`. The app needs yt-dlp 2026.07.04 or newer. |
| [`deno`](https://community.chocolatey.org/packages/deno) | 2.9.8, no dependencies | |

### ffprobe: confirmed

The `ffmpeg` package page (https://community.chocolatey.org/packages/ffmpeg)
lists its files: `tools\ffmpeg-release-essentials.7z` (SHA256
`4705843CCAAF54257C16AD90F3E952ECE33C17DF964ECF7BFDBB0F49C7171077`) and a
`chocolateyInstall.ps1` that unzips it into the package's `tools\ffmpeg`
folder. Its notes say it is "the stable static essentials ffmpeg version"
from gyan.dev, and its VERIFICATION points at
`https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z`.

The gyan.dev builds page (https://www.gyan.dev/ffmpeg/builds/) says its
packages contain "binaries of ffmpeg, ffprobe and ffplay", and names
`choco install ffmpeg` as the release essentials build. All its builds are
64-bit, static, GPLv3, for Windows 10 or later.

So `choco install ffmpeg` brings `ffmpeg.exe`, `ffprobe.exe` and
`ffplay.exe`. Chocolatey shims the executables in a package's folder onto
`PATH`. Still check on the test machine:

```powershell
where.exe ffmpeg
where.exe ffprobe
ffprobe -version
```

Don't add a separate `ffprobe` package.

## What the app does with them today

- **Deno**: used for YouTube when found in Settings, Streaming, Link
  Resolution, **JavaScript runtime**, else on `PATH`. A Start-menu launch
  right after install may still have the old `PATH`; test that.
- **yt-dlp**: the app uses its **built-in** yt-dlp module unless
  **External yt-dlp** is set (full path, or `yt-dlp` for `PATH`). Installing
  the Chocolatey package doesn't change that. Don't change the user's
  setting from the install script.
- **ffmpeg / ffprobe**: nothing in the app runs them yet. They're for the
  planned separate-audio merge. The dependency is there so it works the day
  that lands.

Uninstalling `gridplayer-alabaster` must not remove these shared packages.

## Install script

`tools/chocolateyinstall.ps1` downloads the exact release installer by URL
and SHA256 and runs it with `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-`.
Uninstall uses Chocolatey's auto-uninstaller (matching `softwareName`).

Before packing:

1. Pick the release version; use the same string in the app, the installer
   file name, the nuspec `<version>` and the release tag.
2. Build the installer, upload it to a release, and fill in the real
   `url64bit` and SHA256 in `tools/chocolateyinstall.ps1` and
   `tools/VERIFICATION.txt`. No placeholders in a package that leaves the
   machine.
3. Point every URL in the nuspec at `XDevMatt/alabaster-gridplayer`.
4. Give the installer its own Inno `AppId` and default folder. It still
   has upstream GridPlayer's, so it would install over upstream. The
   Chocolatey auto-uninstaller would then match the wrong entry too.
5. Replace the "Optional tools, install them yourself" text in the nuspec
   description: the three tools are now dependencies.

## Do not use the legacy generator

`scripts/chocolatey/build.sh` is upstream's. It builds packages named
`gridplayer`, `gridplayer.install` and `gridplayer.portable`, and downloads
upstream's release assets (`APP_REPO_SLUG=vzhd1701/gridplayer` in
`scripts/init_app_vars.sh`). **Don't run it.** Retire it, or rewrite it to
produce only `gridplayer-alabaster` from Alabaster's own release.
`packaging/chocolatey/` is the one source for the package.

## Test locally (Windows, admin PowerShell)

```powershell
cd packaging\chocolatey
choco pack
choco install gridplayer-alabaster --source "'.;https://community.chocolatey.org/api/v2/'" -y
where.exe ffprobe ; where.exe deno ; where.exe yt-dlp
choco upgrade gridplayer-alabaster --source "'.;https://community.chocolatey.org/api/v2/'" -y
choco uninstall gridplayer-alabaster -y
```

The second source is needed so the dependencies resolve. Check that the
app starts from the Start menu, plays a local file, plays a YouTube link,
and that uninstall leaves ffmpeg, yt-dlp and Deno in place.

## Out of scope

- No push to the community repository without the maintainer's go.
- No Scoop manifest.
- No PyPI package, ever.
