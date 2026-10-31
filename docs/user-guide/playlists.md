# Playlists and snapshots

## Playlists

A playlist is saved as a `.gpls` file. Alabaster writes it as JSON; older
GridPlayer playlists in the legacy text format can still be opened. A playlist
holds the cells (videos and their per-cell settings), the grid layout, the
window position, snapshots, bookmarks, media lists, and Alabaster per-cell
profiles. See [Where things are stored](../reference/storage.md).

!!! note "To be written"
    Saving, opening and recent playlists are not documented yet.

## Randomized playlist

**Randomize List** (`Ctrl+Shift+N`) shuffles the order of the list a list cell
is playing.

!!! note "To be written"
    Details of list order and how it is kept are not documented yet.

## Snapshots

A snapshot stores the state of the grid in one of ten slots (0 to 9), saved
with the playlist.

| Action | Keys |
| --- | --- |
| Save snapshot to slot 0-9 | `Ctrl+Alt+0` ... `Ctrl+Alt+9` |
| Load snapshot from slot 0-9 | `Ctrl+0` ... `Ctrl+9` |

If the grid no longer matches the snapshot (for example, cells were closed),
the snapshot is applied to the cells still there and a warning shows
**Snapshot applied to N of M cells**.
