# Per-cell settings

Each cell keeps its own settings: file, position, loop points, speed,
volume and mute, zoom, crop, alignment, aspect ratio, transform,
deinterlacing, audio and subtitle tracks and delays, When Finished, Include
Subfolders, Files to Play, slide duration, Other Orientation, list settings,
stream quality and network-error handling.

## Where they come from

- A **new cell** starts from Settings, Defaults, **New Videos**. See [New cells](new-cells.md).
- Anything you change on a cell's menu changes that cell only.
- `[ALL]` on the menu changes every cell at once.

## Saving them

Save the grid as a playlist (`Ctrl+S`) and every cell's settings are saved
with it, each under the cell's own id. Ids stay the same when you move cells
around, shuffle the grid or reopen the playlist, so each cell keeps its own
settings.

A few things are saved only when you ask (Settings, Defaults, Playlist,
Saving / Restoring):

- **Save videos playback position** (off by default)
- **Save videos playback status** (playing / paused; off by default)
- **Save window position and size** (off by default)
- **Save all settings in the playlist** (off): writes every Playlist and New
  Videos default into the playlist, so it plays the same on another PC and
  later changes to your defaults don't reach it.
- **Save video paths relative to playlist file** (off): move the playlist
  together with its videos.

## Playlist-wide settings

Right-click, **Playlist Settings > Edit Playlist Settings…** opens the same
Playlist and New Videos pages as Settings, but the values are the open
playlist's own. They're saved in the `.gpls` file.

!!! note "Cell profiles"
    Alabaster's playlist format also has a per-cell **profile** section keyed
    by cell id. Today it's read only for the Other Orientation choice of
    playlists saved by earlier Alabaster builds; setting it from the menu
    moves it into the cell's normal settings. Its other fields are reserved
    and have no menu or settings yet.
