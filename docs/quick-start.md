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
    ffmpeg and ffprobe are not bundled yet; they are planned. Deno is
    bundled only if the build added it, which the automated build doesn't
    do yet.
    The `portable_data` folder inside keeps your settings and logs next to the
    app.

3.  Open the `GridPlayer` folder and run `GridPlayer.exe`.

4.  Drag video files onto the window. Each file gets its own cell.
    If you drag a folder instead, you get one cell that plays the files in the
    folder and its subfolders as a playlist.

5.  Click a cell to play or pause it. `Ctrl+Space` also works.

That's it. You now have a playing grid. New cells start muted: scroll the
mouse wheel up over a cell to hear it.

!!! note
    The build can also make an installer (`GridPlayer-<version>-win64-install.exe`),
    but none has been published yet. For now, use the portable zip.

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
