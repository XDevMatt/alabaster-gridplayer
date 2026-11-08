# Lists (single-cell playlists)

A **list** is a list of files and links that one cell plays through, in
order, with its own window to edit it. Several cells can play from the same
list, for example four cells on four channels of one IPTV list.

## Make or open a list (`L`)

Point at a cell and press `L` (or right-click, **Playback > List…**).

- If the cell already plays a list, its **List** window opens.
- If it plays a single file, you're asked what to make the list from: the
  file's **folder** (with or without subfolders) or just **this video**.

A dropped M3U / M3U8 / PLS / XSPF file, a folder, or a link to a playlist
(a YouTube playlist, a web M3U, ...) also makes a cell with a list.

## The List window

- **Play in This Cell**, **Open in a New Cell**, **Open in a New Cell as a
  New List**.
- **Add Files…**, **Add Folder…**, **Add Links…**, **Paste**, **Remove**,
  **Move to Top / Bottom**, **Rename**.
- **Sort** by name, length, views, date published or group, **Reverse**,
  **Randomize**, or back to **Source Order**.
- **Find on the list**, **View** as titles, titles and paths, or paths, with
  thumbnails for lists from sites like YouTube.
- **Get Info** looks up titles, lengths and thumbnails (or turn on **Get info
  automatically** in Settings, Defaults, Playlist, Lists).
- **Copy Title / Path / Link**, **Copy All**, **Show in Folder**.
- **Export…** saves the list as an M3U file for other players.

## Linked lists

A list made from a folder, a playlist file or a link can stay **linked** to
its source and update from it, so new files show up:

- When: **On playlist load** (default), every 5 / 15 minutes, every hour,
  every 6 hours, every day, or **Manually** (Settings, Defaults, Playlist,
  Lists, **Update linked lists**; each list can override it).
- **Refresh** updates now and shows what's new and what's gone.
- Only your own changes are saved; the rest comes from the source.
- **Unlink** to edit it freely; **Link to Source** to link it again.

## Playing a list

- `N` / `B` go to the next / previous item; `Shift+N` plays a random one
  (avoiding [files open in other cells](skip-open.md)), `Shift+B` goes back.
- **Randomize List** (`Ctrl+Shift+N`) shuffles the list once, keeping the
  playing item first. Next then goes straight down the new order.
- **At the End of the List**: **Start Over** (default), **Pause At Start**,
  **Stop** or **Close**.
- **When Video Fails**: **Play Next** (default, after 2 seconds) or **Show
  Error**.
- **Leave the List** puts the cell back to stepping through the playing
  file's folder.

Lists are saved with the playlist. See also **Playlist Settings > Lists in
Playlist…** for every list the open playlist has.

## Size limit

M3U, PLS and XSPF lists bigger than **M3U size limit** (Settings, General,
Player, Memory; default 512 MB) aren't loaded. Alabaster's own `.gpls`
playlists have no limit.
