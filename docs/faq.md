# FAQ and troubleshooting

More detail on every feature is in the [User guide](USER-GUIDE.md). Known
rough edges are in [Known limitations](KNOWN-LIMITATIONS.md).

## Is this the official GridPlayer?

No. GridPlayer Alabaster is built from [GridPlayer](https://github.com/vzhd1701/gridplayer)
0.5.5 by Vlad (vzhd1701), with its own changes. Credit for GridPlayer goes
to Vlad. Report Alabaster problems in the
[GridPlayer Alabaster repository](https://github.com/XDevMatt/alabaster-gridplayer/issues),
never to upstream.

## Is it on PyPI? Can I `pip install` it?

No. Alabaster is not on PyPI and never will be from this project.
`pip install gridplayer` and `uv tool install gridplayer` install upstream
GridPlayer. To run Alabaster from code, see [Building from source](building.md).

## What's the license?

GNU GPL version 3, the same as GridPlayer. Alabaster's changes are under the
same terms. See `LICENSE` and `NOTICE` in the repository.

## Does it run on Mac or Linux?

Windows is the only target. Mac, Linux, Snap, Flatpak and translations
aren't project goals. The source is GPLv3, so you're free to port it; for
ready-made Mac or Linux packages, use upstream GridPlayer. See [Platforms](platforms.md).

## Installer or portable ZIP?

- **Installer**: Start menu entry, file associations, uninstall entry.
  Settings in `C:\Users\<user>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster\`.
- **Portable ZIP**: unzip anywhere, nothing installed, settings in the
  `portable_data` folder next to `GridPlayer.exe`. Good for a USB stick or
  for trying it out.

Neither is published yet. See [Install on Windows](install.md).

## Do I need to install VLC?

No. The Windows build has its own libVLC. (Running from source is different:
see [Building from source](building.md).)

## Do I need ffmpeg, yt-dlp or Deno?

Not for local files, folders or most links.

- **Deno**: install it if YouTube links stop playing.
- **yt-dlp.exe**: optional; the app has yt-dlp built in. Use your own only if
  you want to update it yourself, and set **External yt-dlp** in Settings.
- **ffmpeg / ffprobe**: nothing uses them yet. They're for a planned
  separate-audio merge.

The planned Chocolatey package `alabaster-gridplayer` will pull in all three.
See [Install on Windows](install.md#whats-in-the-box-and-what-isnt).

## Can I keep upstream GridPlayer installed?

Yes. Alabaster uses its own settings folder (`GridPlayer-Alabaster`, next
to upstream's `GridPlayer`) and its own single-instance channel, so neither
one picks up the other's settings or "Open with" files.

The installer recipe also has its own installer id, install folder
(`C:\Program Files\GridPlayer Alabaster\`) and Start menu folder, so
installing or uninstalling Alabaster leaves upstream GridPlayer alone. No
installer has been published yet.

## I typed `gridplayer` and got a different version

If upstream GridPlayer is installed with pip or uv, the `gridplayer`
command on your `PATH` starts upstream. Run Alabaster's own
`GridPlayer.exe`, or `.\.venv\Scripts\gridplayer.exe` from a source checkout.

## Nothing happens when I press a key

Keys act on the cell under the mouse pointer. With the pointer outside every
cell (on the title bar, for example), cell keys do nothing. Move the pointer
over a cell and try again.

## New videos are silent

That's on purpose: new cells start muted. Scroll up over a cell, or press
`M`. To change it, turn off **Muted** in Settings, Defaults, New Videos,
Audio. See [New cells](user-guide/new-cells.md).

## `E` (Keep) does nothing

Keep only works in **Single Mode** (double-click a cell first) and only on a
local file, not a link. See [Keep](user-guide/keep.md).

## YouTube says "Sign in to confirm you're not a bot"

Pick your browser in Settings, Streaming, Cookies, while you're signed in to
YouTube in that browser. See [Streaming](user-guide/streaming.md#cookies).

## YouTube links stopped working

Install Deno, restart, and use **Test a YouTube link** in Settings,
Streaming, Link Resolution. If you use an external yt-dlp, update it.

## Where are my settings, logs and screenshots?

Settings, at the bottom: **Open data folder**. See
[Data folder and portable mode](reference/data-folder.md).

## How do I start over with default keys?

Settings, Shortcuts page, **Reset all**. Changed keys are stored as differences from the
defaults, so resetting there brings back the defaults.

## Why does unmute start so quiet?

Mute is volume 0%, and nothing is kept behind it. Unmuting starts at one
volume step (3% by default). Change the step in Settings, General, Player,
**Volume step per wheel notch or key press**. For a mute that keeps your
level, use the Windows or speaker mute.

## Is `K` Keep?

No. Keep is `E`. `K` is Audio Delay Later.

## Where did my kept file go?

Keep copies the file into a folder next to the video's folder, named after it
with `_keep` added: `D:\Clips\Cats\a.mp4` goes to `D:\Clips\Cats_keep\a.mp4`.
If a file of that name is already there, nothing is copied. The log
(`gridplayer.log`) records each Keep.

## F4 renamed the title but not the file.

`F4` changes only the title shown in Alabaster. It never renames the file on
disk. A disk rename is planned for `F2`.

## Rotate keys V and M do nothing.

The transform commands have no default keys. Assign them in the Shortcuts
editor; see [Suggested transform keys](reference/keyboard-shortcuts.md#suggested-transform-keys-not-defaults).
`M` is mute-all by default.

## My playlist shuffles every time it opens.

Shuffle On Load is off by default, but a playlist saved with it on keeps its
own value. Open the playlist, untick **Grid > Shuffle On Load**, and save it.

## Audio files or pictures from a dropped folder are missing.

**Files to play** is **Videos only** by default. Set it to **All media** (or
**Images only**) in Settings, Defaults, New Videos, Playback, or per cell under
**Playback > Files to Play**, then drop the folder again.

## Random play skips some files.

**Skip files open in other cells** (on by default) skips files already open in
another cell. **Other orientation: Skip it** skips files of the wrong shape for
the cell.

## Why is the best YouTube quality missing?

Higher YouTube qualities are often separate DASH video and audio files, which
Alabaster cannot pair yet. Only formats that play with sound are offered.

## The SubtitleCat.com item is not on the menu.

The plugin is off by default. Turn on Settings, Plugins, **Enable
SubtitleCat.com**. You also need to be signed in to subtitlecat.com in the
browser chosen on the Cookies page.

## Panes go grey or stutter.

Set **Videos per process** to 1 (Settings, Advanced, Video Decoder). Avoid
running another hardware-decoding player on the same integrated GPU. Try
Hardware SP or Software.

## How do I run it from source?

From the repository folder, after `uv sync`:

```powershell
.\.venv\Scripts\gridplayer.exe
```
