# Playlists and snapshots

Alabaster uses the word *playlist* for two things:

- A **saved playlist** (`.gpls` file) stores your whole grid so you can open it
  again later.
- A **playlist cell** is one cell that plays a list of files, for example a
  folder you dropped on the grid.

## Save your grid as a playlist

A saved playlist is a `.gpls` file. It holds:

- the cells (videos and their per-cell settings)
- the grid layout
- the window position, when **Save window position and size** is on
- snapshots
- bookmarks
- media lists
- Alabaster per-cell profiles

Alabaster writes `.gpls` files as JSON. You can still open older GridPlayer
playlists saved in the legacy text format.

For where these files live, see [Where things are stored](../reference/storage.md).

All of these are on the right-click menu:

| To do this | Menu item | Key |
| --- | --- | --- |
| Save the grid | **Save Playlist** | `Ctrl+S` |
| Save it under another name | **Save Playlist As** | `Ctrl+Shift+S` |
| Open a saved playlist | **Open Playlist** | `Ctrl+O` |
| Open one you used lately | **Recent Playlists** | |
| Close the playlist | **Close Playlist** | `Ctrl+Shift+Q` |

**Recent Playlists** is there while **Enable recent list** is on (Settings,
General, Player, History; on by default). It keeps the last 10, which you can
change with **Maximum size**. **Reopen last playlist on startup** (off by
default) opens the last one when the app starts.

What happens to unsaved changes when you close is the **Unsaved changes on
close** setting (Settings, Defaults, Playlist, Saving / Restoring). The default
is **Discard Changes**, so save before you close.

## Play a folder

Drag a folder onto the grid. You get one cell that plays the media files in
that folder and in its subfolders as a playlist, in name order. Videos, audio
files and pictures all go on the list.

### Choose which files play

The **Files to play** setting decides which files of a folder
**Next**, **Previous** and **Play Random File** go on to when a cell plays a
single file from that folder. It doesn't filter the list of a folder you
dropped.

It is in Settings, Defaults, New Videos, Playback, and for one cell on the
right-click menu under **Playback > Files to Play**. The choices are:

- **All media**: every media file: videos, audio and pictures.
- **Videos only** (the default): video files only. Audio files and pictures
  are skipped.
- **Images only**: pictures only.

### Include subfolders

A folder you drop is always read with its subfolders.

**Include subfolders** (`video_defaults/dir_recursive`, off by default) is for
a cell that plays a single file: when it's on, **Next**, **Previous** and
**Play Random File** also go through the subfolders of that file's folder.
It is in Settings, Defaults, New Videos, Playback, and on the right-click menu
under **Playback**.

### Scan limit for large folders

When Alabaster reads a folder and its subfolders, it stops after it has looked
at a set number of items. This keeps the app from hanging if you drop a whole
drive by mistake.

The setting is **Scan limit**, in Settings, Defaults, Playlist, Folder
Navigation.

| Setting key | Default | Range |
| --- | --- | --- |
| `playlist/folder_max_entries` | `50000` | `0` to `1000000`. `0` means no limit. |

Keep in mind:

- The limit counts every file **and** folder looked at, not only media files.
- Only media files are added: videos, audio and pictures.
- The limit applies to every folder read with its subfolders: a dropped
  folder, **Add Folder**, and **Next**, **Previous** and **Play Random File**
  while **Include subfolders** is on.

## Use a randomized playlist

There are two different commands.

**Play Random File** (`Shift+N`) plays another file at random. It goes through
every entry once, in random order, before any entry repeats. This is not
true shuffle, where the same file can come up twice in a row. With **When
finished** set to **Play random file**, the cell does this by itself at the
end of each file.

How it works:

- **Each cell has its own order.** Playing at random in one cell doesn't
  affect others.
- **Every entry plays once per round.** When the round ends, a new random
  order starts. In a playlist cell, that happens only when **When list ends** is
  **Start over** (the default); otherwise the list ends as that setting says.
- **New files join the current round.** Files added mid-round are placed at
  random among the entries not yet played.
- **You can step back.** Press `Shift+B` to go back through what already
  played.
- **The order isn't saved.** It lasts only while the app is open.

**Randomize List** (`Ctrl+Shift+N`, on the right-click menu under **Playback**
in a playlist cell) puts the cell's list itself in a random order once, with the
item playing at the top. **Next** then plays straight down the new order, which
stays with the list.

## Save and restore grid states (snapshots)

A snapshot stores the state of the grid in one of ten slots, `0` to `9`.
Snapshots are saved with the playlist.

| To do this | Press |
| --- | --- |
| Save a snapshot to slot 0-9 | `Ctrl+Alt+0` ... `Ctrl+Alt+9` |
| Load a snapshot from slot 0-9 | `Ctrl+0` ... `Ctrl+9` |

If the grid no longer matches the snapshot (for example, you closed some
cells), Alabaster applies the snapshot to the cells that are still there and
shows a warning: **Snapshot applied to N of M cells**.
