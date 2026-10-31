# Quick start

!!! note "To be written"
    Installer downloads and first-run screenshots are not written yet.

## Run from source (Windows)

You need [uv](https://docs.astral.sh/uv/) and [VLC](https://www.videolan.org/)
installed. See [Building from source](building.md) for details.

```powershell
uv sync
.\.venv\Scripts\gridplayer.exe
```

`uv run gridplayer` also works from the repository folder.

## First steps

- Drag video files or a folder onto the window. Each file gets a cell.
- Click a cell to play or pause it (`Ctrl+Space` also works).
- `N` / `B` (or `PgDown` / `PgUp`) play the next / previous file in a cell.
- Right-click for the menu; **Shortcuts** there lists every key.

See [Hotkeys](reference/hotkeys.md) for the full list.
