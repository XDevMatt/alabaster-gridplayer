# Configuration and files

This page explains where GridPlayer Alabaster keeps its settings and other
files, which command-line options it accepts, and how a cell gets its values.
For the list of every setting with its default and range, see
[Settings](settings.md). For where each setting is kept (global file,
playlist, or per cell), see the [full settings reference](settings-reference.md).

Alabaster supports Windows only. Some generated reference pages mention macOS
or Linux behavior because the code is shared with upstream GridPlayer; those
notes do not mean Alabaster supports those systems.

## The data folder

All of Alabaster's own files live in one **data folder**. It is chosen in this
order:

1. `--user-data-dir <folder>` on the command line.
2. The `GP_USER_DATA_DIR` environment variable.
3. **Portable mode**: a folder named `portable_data` next to `GridPlayer.exe`
   (packaged builds). If it exists, it is used.
4. The normal location: `%APPDATA%\vzhd1701\GridPlayer-Alabaster`
   (for example `C:\Users\<user>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster`).

A relative path in options 1 or 2 is resolved against the current working
directory. The command-line option wins over the environment variable.

The folder is Alabaster's own. Upstream GridPlayer uses
`%APPDATA%\vzhd1701\GridPlayer`. Alabaster does not read or copy upstream's
settings; it starts with its own defaults.

**Settings > Open data folder** opens the folder in Explorer.

### What is in it

| File or folder | What it is |
| --- | --- |
| `settings.ini` | All global settings (Qt INI format). Written when you click OK in Settings and when the app changes a stored value. |
| `gridplayer.log` | The log. Rotated only when **Limit log file size** is on. |
| `screenshots\` | Default screenshot folder. |
| `media_shapes.json` | Cache of which files are portrait or landscape, used by the Other orientation filter. Safe to delete. |
| `subtitles\` | SubtitleCat.com downloads, when the video's own folder cannot be written. |
| `cache\` | Thumbnails and downloaded lists, **only** in portable mode or with a moved data folder. Otherwise the cache is in `%LOCALAPPDATA%\vzhd1701\GridPlayer-Alabaster\cache`. With **Cache: In memory**, nothing is written. |
| `cookies.txt` | Only if left over from an older build. Not read, not deleted. |

### Keys in settings.ini that are not in the Settings window

| Key | Meaning |
| --- | --- |
| `recent_list_videos`, `recent_list_playlists` | The Recent lists. |
| `last_playlist` | Used by **Reopen last playlist on startup**. |
| `player/tray_note_shown` | The tray notice was shown once. |
| `player/keymap` | Your shortcut changes, stored as differences from the default keymap. |
| `migrations/volume_step_3` | One-time marker: a saved 5% volume step was moved to 3%. |

### Resetting

- One page: the reset button on that Settings page.
- Shortcuts: **Reset all** in the Shortcuts editor.
- Everything: quit Alabaster and delete or rename `settings.ini`.

## Command line

```text
GridPlayer.exe [options] [FILE|URL ...]
```

From source, use `.\.venv\Scripts\gridplayer.exe` or `uv run gridplayer`.

| Option | Description |
| --- | --- |
| `--user-data-dir PATH` | Store settings, logs and the rest of the data folder in `PATH`. |
| `--version` | Print `GridPlayer Alabaster <version>` and exit. |
| `--help` | List the options and exit. |
| `--` | End of options. Use it before a file name that starts with `-`. |

Any other argument is a thing to open: a media file, a folder, a `.gpls`
playlist, a media list (`.m3u`, `.m3u8`, `.pls`, `.xspf`), or a link. A folder
or a media list plays in one cell. Unknown options are rejected with an error.

If Alabaster is already running and **Allow only one instance** is on, the
arguments are sent to the running window (see below) and the new process
exits.

## Single instance

With **Allow only one instance** on (the default), the first Alabaster window
listens on the named pipe `\\.\pipe\gridplayer-alabaster-fileopen`. A second
start sends its files there as a length-prefixed JSON message and exits. The
listener accepts only that format (an old pickle message is refused), limits
a message to 1 MB and 1,024 items, and does not wait on a client that sends
nothing.

Upstream GridPlayer uses a different pipe (`gridplayer-fileopen`), so the two
programs never receive each other's files.

## Windows registry

Alabaster itself writes nothing to the registry. It reads:

- `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme`
  when Color scheme is System.
- Where VLC is installed, when running from source without a bundled VLC.

The **installer** (when one is published) writes file associations for media
files and `.gpls` playlists, a Start menu entry, and its uninstall entry. The
portable zip writes nothing.

## Saved playlists (.gpls)

A playlist is a JSON file. It is written only when you save (or when
**Unsaved changes on close** auto-saves). It contains:

| Part | Holds |
| --- | --- |
| `settings` | The playlist's own values for Playlist and New Videos settings. Normally only values that differ for this playlist; with **Save all settings in the playlist**, all of them. Also `grid_state` (layout), `window_state` (when **Save window position and size** is on), and snapshots. |
| `videos` | One entry per cell: its id, file or link, and its own copy of every New Videos value, plus volume, zoom, crop, transform, tracks, delays, loop points, title, color, list and position in it, and position and play state when those save options are on. |
| `cell_profiles` | Extra per-cell options keyed by the cell's id (see below). |
| `bookmarks` | Bookmarks, per file. |
| `lists` | Media lists (folder, file, link, channel lists) used by cells. |

Older GridPlayer text playlists can still be opened. Playlists saved by
Alabaster cannot be opened by GridPlayer 0.5.x or older.

### Stable cell ids and per-cell profiles

Each cell has a UUID (`id` in its `videos` entry) that never changes for the
life of the cell, including through save and load, reordering, Shuffle and
snapshots. `cell_profiles` maps those ids to profile objects, so a profile
always follows its cell. Profiles of cells that no longer exist are dropped
when the playlist is saved.

A profile can hold `aspect_filter`, `end_action`, `loop`, `upscale`,
`downscale`, `deband` and `sources` (weighted source folders). In this
version the player reads only `aspect_filter`: a value saved there by an
earlier build wins over the cell's own setting until you pick a new Other
orientation choice from the menu, which clears it. The other fields are kept
in the file but have no effect and no user interface yet.

## How a cell gets its values

1. When a cell is created, it takes each New Videos value from the open
   playlist if the playlist has its own value, otherwise from `settings.ini`.
2. From then on the cell has its own copy. Changing a default later does not
   change existing cells.
3. The cell's copy is saved only in a saved playlist. Without one, closing the
   app loses it, and the next cells start from the defaults again.

Playlist-level values (grid, sync, overlay, input, pause options) work the
same way at the playlist level: a playlist that has its own value keeps it
until you change it there. This is why a playlist saved with **Shuffle On
Load** on keeps shuffling until you untick it and save that playlist again.
