# Dropping folders

Drag a folder from Explorer onto the window (or use **Add > Add Folder**) and
you get a cell that plays the folder's files one after another.

## Which files go in

The cell takes the files that match its **Files to Play** setting:

| Files to Play | What goes in |
| --- | --- |
| **Videos only** (default) | Video files only. Audio files and pictures are left out. |
| **All media** | Videos, audio files and pictures. |
| **Images only** | Pictures only, shown as slides. |

The default is in Settings, Defaults, New Videos, Playback, **Files to
play**. To change it for one cell, right-click, **Playback > Files to Play**;
for every cell, **[ALL] > Playback > Files to Play**.

Files you drop one by one are always taken, whatever this says: a picture or
an audio file dropped on its own still opens.

## Subfolders

With **Include subfolders** on (the default), the folder's subfolders are
read too, depth first in name order. Turn it off in Settings, Defaults, New
Videos, Playback, or per cell with right-click, **Playback > Include
Subfolders**. Hidden and system folders are skipped (Settings, Defaults,
Playlist, Folder Navigation, **Skip hidden and system files**).

## How many cells

Settings, Defaults, Playlist, Drag-n-Drop, **Cells**:

- **One per item** (default): each dropped file and each dropped folder gets
  its own cell. A folder becomes one cell playing it as a list.
- **One for all**: everything you drop goes into one cell.
- **One per video**: every video gets its own cell, even inside folders and
  playlists. Careful with big folders.
- **Ask**: choose each time.

Adding more than 12 cells at once asks first (**Warn above**).

## Very large folders

Reading stops after **Scan limit** entries (default 50,000; every file and
folder counts, not just media). That keeps a drop of a whole drive from
hanging the app. See [Folders](folders.md#scan-limit).

## Drop onto a cell, or between cells

- **File drop** (Settings, Drag-n-Drop): **Add** (default) adds new cells;
  **Replace** puts the dropped item in the cell you drop on.
- Hold `Shift` while dropping to do the other one.
- Dropping **subtitle files** on a cell adds them to that cell instead. See
  [Subtitles](subtitles.md).
