# Folders

Drop a folder on the window to play the files in it. Each cell then moves
through files by itself:

- **Next** / **Previous** (`N` / `B`, `PgDown` / `PgUp`) stay in the playing
  file's folder. With **Include Subfolders** on, they cover that cell's root
  folder and its subfolders. Include Subfolders is on by default.
- **Random** (`Shift+N`) picks from the same set of files. **Back to Previous
  Random File** is `Shift+B`.
- **Next** on the last file wraps around to the first file.

The full walk-through, including what is skipped, is in
[Moving between files](navigation.md).

## Scan limit

Settings, Playlist page: **Scan limit** (`playlist/folder_max_entries`,
default **50000**, 0 = no limit, maximum 1000000). With subfolders included, it
caps how many files and folders are looked through (everything counts, not
just videos), so a drop of a whole drive does not hang the app.
