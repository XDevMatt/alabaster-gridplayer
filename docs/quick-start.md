# Quick start

This page gets you from download to a grid of playing videos in five steps.
GridPlayer Alabaster is built and tested mainly on Windows 10 and 11. For other
systems, see [Platforms](platforms.md).

## Play your first grid (Windows)

1.  Download the Windows portable zip from the
    [Releases page](https://github.com/XDevMatt/gridplayer-alabaster/releases).
    No release has been published yet. When one is, the zip will be named
    `GridPlayer-<version>-win64-portable.zip`, for example
    `GridPlayer-0.5.5-win64-portable.zip`.

2.  Extract the zip to a folder you own, for example `C:\Tools\GridPlayer-Alabaster`.
    The zip holds one folder, `GridPlayer`. VLC (libVLC), yt-dlp and
    Streamlink are inside it, so you don't need to install VLC.
    ffmpeg, ffprobe, the yt-dlp program and Deno are not bundled; see
    [Requirements](#requirements).
    The `portable_data` folder inside keeps your settings and logs next to the
    app.

3.  Open the `GridPlayer` folder and run `GridPlayer.exe`.

4.  Drag video files onto the window. Each file gets its own cell.
    If you drag a folder instead, you get one cell that plays the files in the
    folder (and its subfolders when **Include subfolders** is on) as a playlist.

5.  Click a cell to play or pause it. `Ctrl+Space` also works.

That's it. You now have a playing grid. New cells start muted: scroll the
mouse wheel up over a cell to hear it.

!!! note
    The build can also make an installer (`GridPlayer-<version>-win64-install.exe`),
    but none has been published yet. For now, use the portable zip.

## Requirements

Alabaster bundles VLC (libVLC), which plays everything, plus the yt-dlp and
Streamlink Python modules it resolves links with. It does **not** bundle
the command-line tools below. You install them yourself and keep them
updated, because sites change often and an old copy stops working.

| Tool | Needed for | Required? |
| --- | --- | --- |
| **ffmpeg** and **ffprobe** | Streams whose sound comes as a separate file that VLC can't pair by itself (YouTube's DASH formats among them). That merge is planned; no current feature runs ffmpeg or ffprobe yet. | Required for those streams once the feature lands |
| **yt-dlp** (the program) | Using a yt-dlp you update yourself instead of the built-in module | Optional |
| **Deno** | YouTube's JavaScript challenge, which yt-dlp needs a JavaScript engine for | Optional, for YouTube streaming |

Install them on Windows with winget:

```
winget install Gyan.FFmpeg
winget install yt-dlp.yt-dlp
winget install DenoLand.Deno
```

On macOS with Homebrew:

```
brew install ffmpeg yt-dlp deno
```

On Linux use your distribution's packages. Update them the same way
(`winget upgrade --all`, `brew upgrade`, or `yt-dlp -U` for a standalone
yt-dlp), then restart Alabaster.

### Where Alabaster finds them

- **Deno**: the folder in Settings, Streaming, Link Resolution,
  **JavaScript runtime**, else `deno` on your PATH. If neither has one,
  YouTube links that need it fail and **Test a YouTube link** in the same
  place says so.
- **yt-dlp**: set Settings, Streaming, Link Resolution, **External yt-dlp**
  to the full path of the program (for example
  `C:\Users\you\AppData\Local\Microsoft\WinGet\Links\yt-dlp.exe`), or
  just to `yt-dlp` to use the one on your PATH. Left empty, or if the
  program isn't found, Alabaster uses its built-in yt-dlp module.

## Learn a few basics

Keys act on the cell under the mouse pointer.

| To do this | Do this |
| --- | --- |
| Play or pause a cell | Click the cell, or press `Ctrl+Space`. |
| Play the next file in a cell | Press `N` or `PgDown`. |
| Play the previous file in a cell | Press `B` or `PgUp`. |
| Change a cell's volume | Scroll the mouse wheel over the cell. |
| Mute or unmute all cells | Press `M`. |
| Show one cell on its own | Double-click the cell. Double-click again to go back. |
| See every command and key | Right-click, then choose **Shortcuts**. |

For the full key list, see [Hotkeys](reference/hotkeys.md).

## Next steps

- [The grid](user-guide/grid.md): control cells and switch to Single Mode.
- [Playlists and snapshots](user-guide/playlists.md): play folders, save your
  grid, and jump between saved layouts.
- [Volume](user-guide/volume.md): set volume per cell and mute everything.
- [Platforms](platforms.md): what runs where.

## Run from source (Windows)

If you'd rather run the code directly, install [uv](https://docs.astral.sh/uv/)
and [VLC](https://www.videolan.org/) first. See
[Building from source](building.md) for details.

From the repository folder, run:

```powershell
uv sync
.\.venv\Scripts\gridplayer.exe
```

`uv run gridplayer` also works from the repository folder.
