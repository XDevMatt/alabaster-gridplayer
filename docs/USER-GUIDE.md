# GridPlayer Alabaster user guide

This guide covers every feature of GridPlayer Alabaster that a user can see or
use. It describes the `0.2beta-fixes` branch, which is the version being
prepared for the first public beta ("Alabaster 0.2beta - (from GridPlayer
0.5.5)"). The About window still shows the internal version string
`0.5.5-alabaster.1`.

GridPlayer Alabaster is a modified version of
[GridPlayer](https://github.com/vzhd1701/gridplayer) 0.5.5 by Vlad
(vzhd1701). It is licensed under the GNU GPL version 3, the same as
GridPlayer. It is not the official GridPlayer, and it is not on PyPI.
Alabaster supports Windows 10 and 11 only.

Related pages:

- [Keyboard and mouse shortcuts](reference/keyboard-shortcuts.md): every
  default key, mouse action and drag.
- [Settings](reference/settings.md): every setting with its default, range and
  tooltip (generated from the code).
- [Configuration and files](reference/configuration.md): where settings,
  playlists, logs and caches live, command-line options, and how a cell gets
  its values.
- [Plugins and streaming](PLUGINS-AND-STREAMING.md): yt-dlp, browser cookies,
  HLS and DASH, separate audio, SponsorBlock and SubtitleCat.com.
- [Known limitations](KNOWN-LIMITATIONS.md).
- [Future features](FUTURE.md).

## Contents

1. [Install and start](#1-install-and-start)
2. [How the window works](#2-how-the-window-works)
3. [Adding videos](#3-adding-videos)
4. [The grid](#4-the-grid)
5. [Playing, pausing and seeking](#5-playing-pausing-and-seeking)
6. [Moving between files in a cell](#6-moving-between-files-in-a-cell)
7. [Lists in a cell](#7-lists-in-a-cell)
8. [Loops and When finished](#8-loops-and-when-finished)
9. [Volume and audio](#9-volume-and-audio)
10. [Subtitles](#10-subtitles)
11. [Picture: zoom, view mode, aspect, crop, position](#11-picture-zoom-view-mode-aspect-crop-position)
12. [Transforms and Rotate to fit](#12-transforms-and-rotate-to-fit)
13. [Other orientation (aspect filter)](#13-other-orientation-aspect-filter)
14. [Pictures as slides](#14-pictures-as-slides)
15. [Chapters, bookmarks and SponsorBlock](#15-chapters-bookmarks-and-sponsorblock)
16. [Keep, copy, rename and file commands](#16-keep-copy-rename-and-file-commands)
17. [Screenshots](#17-screenshots)
18. [Sync between cells](#18-sync-between-cells)
19. [Saved playlists, per-cell profiles and snapshots](#19-saved-playlists-per-cell-profiles-and-snapshots)
20. [Streaming links](#20-streaming-links)
21. [Shortcuts editor](#21-shortcuts-editor)
22. [Settings window](#22-settings-window)
23. [Window, tray, media keys and screensaver](#23-window-tray-media-keys-and-screensaver)
24. [Single instance and opening files from Explorer](#24-single-instance-and-opening-files-from-explorer)
25. [Video decoder and performance](#25-video-decoder-and-performance)
26. [Troubleshooting](#26-troubleshooting)

---

## 1. Install and start

### Requirements

- Windows 10 or 11, 64-bit.
- VLC is bundled with the Windows build (libVLC 3.0.24). You do not need to
  install VLC to use the packaged build.
- Optional tools you install and update yourself. Alabaster does not bundle
  them:
  - **Deno**: needed for many YouTube links (yt-dlp runs YouTube's
    JavaScript challenge with it). `winget install DenoLand.Deno`
  - **yt-dlp** (the program): only if you want to use a yt-dlp you keep
    updated yourself instead of the built-in module.
    `winget install yt-dlp.yt-dlp`
  - **ffmpeg / ffprobe**: not used by any current feature. They will be needed
    for streams whose audio comes as a separate DASH file once that merge is
    built. `winget install Gyan.FFmpeg`

  With Chocolatey instead: `choco install deno ffmpeg yt-dlp -y`, and
  `choco upgrade deno ffmpeg yt-dlp -y` to update them.

### Ways to get Alabaster

The portable zip is out as release candidate [v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1), a
prerelease. The installer and Chocolatey package are not released yet. You can
also run Alabaster from source.

| Package | Status | Notes |
| --- | --- | --- |
| Portable zip (`GridPlayer-Alabaster-57f21b1-win64-portable.zip`) | [v0.2beta_rc1 prerelease](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1), unsigned | Extract into a new folder and run `GridPlayer-Alabaster-portable\GridPlayer.exe`. A `portable_data` folder next to the program keeps settings and logs with the app. |
| Installer (`GridPlayer-<version>-win64-install.exe`) | Can be built, not released yet | Inno Setup installer. Installs into Program Files, adds a Start menu entry and an optional desktop icon, and registers file associations for media files and `.gpls` playlists. |
| Chocolatey package `gridplayer-alabaster` | Draft only | Downloads and silently runs the installer. It cannot be published until an installer release and its checksum exist. |
| From source | Works now | See [Building from source](building.md). |

`pip install gridplayer`, `uv tool install gridplayer`, `scoop install
gridplayer`, Flathub, the Snap Store and the upstream DMG all install
**upstream GridPlayer**, not Alabaster.

### Run from source

Install [uv](https://docs.astral.sh/uv/) and VLC 3.0 (64-bit), then in the
repository folder:

```powershell
uv sync
.\.venv\Scripts\gridplayer.exe
```

`uv run gridplayer` also works from the repository folder. If you type a bare
`gridplayer` and get an old GridPlayer, that is an upstream copy on your PATH;
run the one in `.\.venv\Scripts\` instead.

### Alabaster next to upstream GridPlayer

Alabaster keeps its own settings folder
(`%APPDATA%\vzhd1701\GridPlayer-Alabaster`) and its own single-instance pipe
(`\\.\pipe\gridplayer-alabaster-fileopen`). Upstream GridPlayer uses
`%APPDATA%\vzhd1701\GridPlayer` and `gridplayer-fileopen`. The two programs can
be installed and run side by side without sharing settings or catching each
other's files.

---

## 2. How the window works

- The main window is the **grid**. Each **cell** plays one video, one picture,
  one audio file, one stream, or one list of items.
- **Keys act on the cell under the mouse pointer** (the "active" cell). Move
  the pointer over a cell before you press a key. With the pointer outside
  every cell, cell keys do nothing. `Tab` and `Shift+Tab` move the active cell
  to the next or previous one without the mouse.
- Most keys that act on one cell have a **Shift** version that acts on every
  cell. For example, `[` sets the loop start in one cell and `Shift+[` sets it
  in all cells. The right-click menu has the all-cells commands under
  **[ALL]**.
- **Right-click** a cell to open its menu. Right-click empty space to get the
  program and grid menus. The menu shows only commands that apply to that cell
  (for example, Chapters appears only when the video has chapters).
- Each cell has an **overlay**: title, play/pause button, volume, a seek bar
  with marks for loops, bookmarks, chapters and SponsorBlock segments, and
  status or error messages. While a video loads, the overlay shows **Stop**;
  after an error it shows **Try Again** and **Details**. The overlay hides
  after 3 seconds without mouse movement (setting **Hide overlay after
  timeout**). **Disable overlay** turns it off entirely.
- The active cell has a border when **Show overlay border for active video** is
  on (the default).
- The mouse pointer hides after 5 seconds without movement (setting **Hide
  mouse after timeout**).
- An empty window shows a drop target. Drop files there or right-click for
  **Add**.

---

## 3. Adding videos

### Ways to add

| Method | How |
| --- | --- |
| Drag and drop | Drag files, folders, playlists or links from Explorer or a browser onto the window. |
| Add Files | Right-click, **Add > Add Files** (`Ctrl+A`). |
| Add Folder | Right-click, **Add > Add Folder**. |
| Add URL(s) | Right-click, **Add > Add URL(s)** (`Ctrl+U`). Paste one link per line. The dialog has a **Paste** button and lists the supported URL schemes and sites. |
| Clipboard | **Add > From Clipboard** (`Ctrl+V`) adds the files or links on the clipboard. |
| Recent | **Add > Recent** lists videos you opened before (setting **Enable recent list**, up to **Maximum size** items, default 10). |
| Explorer | Select files or folders, right-click, **Open with** Alabaster (or double-click when the installer associated the type). See [section 24](#24-single-instance-and-opening-files-from-explorer). |
| Command line | `GridPlayer.exe [options] FILE|URL ...` See [Configuration](reference/configuration.md#command-line). |

What can be added: any media file VLC plays (video, audio, pictures), folders,
Alabaster playlists (`.gpls`), media lists (`.m3u`, `.m3u8`, `.pls`, `.xspf`),
and links (`http`, `https`, `rtsp`, `rtmp`, `mms`, `mmsh`, `rtp`, `udp`, and
others the Add URL(s) dialog lists). Files the player cannot play are skipped.

### How many cells an add makes

Setting **Cells** (Settings, Defaults, Playlist, Drag-n-Drop):

| Choice | Result |
| --- | --- |
| **One per item** (default) | Each file gets its own cell. Each folder or media list gets one cell that plays it as a list. |
| **One for all** | Everything added together goes into one cell as one list. |
| **One per video** | Every video gets its own cell, even the ones inside folders and lists. |
| **Ask** | Alabaster asks each time. |

If an add would create more than **Warn above** cells (default 12), Alabaster
asks first, because too many cells at once can freeze the player. You can tick
**Don't warn again**. While a large folder is being read, a dialog offers
**Stop and add what was found so far**.

### Folders follow Files to play

A folder you drop or add becomes a list of the files it holds, filtered by the
**Files to play** setting (default **Videos only**). With Videos only, audio
files and pictures inside the folder are left off the list. Files you drop one
by one are always taken, whatever Files to play says. With **Include
subfolders** on (the default), the files in subfolders are added too. See
[section 6](#6-moving-between-files-in-a-cell).

### Drop actions and the Shift key

Two settings decide what a drop does (Settings, Defaults, Playlist,
Drag-n-Drop):

- **File drop** (default **Add**): files dropped from outside are added as new
  cells. **Replace** puts the dropped file into the cell you drop on instead.
- **In-window drag** (default **Move / Swap**): dragging a cell onto another
  moves or swaps them. **Replace** copies the dragged video into the target
  cell instead.

Hold the **Hold to switch drop action** key (default `Shift`) while you drop
to do the other action. While dragging, markers show where the video will
land; drop at the edge of a cell to insert before or after it.

### Subtitle files

Dropping subtitle files (`.srt`, `.ass`, `.ssa`, `.vtt`, `.sub`, `.idx`,
`.smi`, `.ttml` and the other types VLC reads) onto a cell does not create a
new cell. The subtitles attach to the video in that cell and the first dropped
file is selected. See [section 10](#10-subtitles).

---

## 4. The grid

### Layout

Right-click, **Grid**. The same choices are in Settings, Defaults, Playlist,
Grid.

| Item | What it does |
| --- | --- |
| **Auto (Rows First)** (default) | Cells fill row by row. The grid grows as you add cells. |
| **Auto (Columns First)** | Cells fill column by column. |
| **Fixed Grid** | A set number of rows and columns (default 3 by 3). Cells stay where you put them and empty places are kept. |
| **Set Size** (Auto modes) | Cells per row (Rows First) or per column (Columns First). Auto (0) keeps the grid as square as possible. |
| **Fit Cells** (Auto modes) | When the last row or column is not full, its cells stretch to fill it. On by default. |
| **Set Grid Size** (Fixed Grid) | Rows and columns. |
| **Show All Cells** (Fixed Grid) | Always show every row and column, with empty cells. Off: the grid shrinks to the cells in use. |
| **Shuffle** (`Alt+R`) | Puts the cells in a random order once. |
| **Shuffle On Load** | Shuffles the cells each time the playlist opens. **Off by default.** |

!!! note "Shuffle on load"
    Shuffle On Load is off by default. A playlist saved while it was on keeps
    its own value. If a playlist still shuffles every time it opens, open it,
    untick **Grid > Shuffle On Load**, and save the playlist again.

### Moving cells

Drag a cell with the left mouse button onto another cell to move or swap it
(see [Drop actions](#drop-actions-and-the-shift-key)). Hold `Shift` while
dropping to replace instead.

### Single mode

Single mode shows one cell filling the window.

- Double-click a cell, or right-click and choose **Enter Single Mode**.
  Double-click again, or **Leave Single Mode**, to return to the grid.
- Other cells pause while hidden when **Pause background videos on single
  mode** is on (the default) and resume when you leave single mode.
- In single mode, **Next Video** and **Previous Video** (media keys
  `Media Next` / `Media Previous`, or the menu) switch to the next or previous
  cell.
- Single mode is offered only when the grid has more than one cell.
- **Keep** (`E`) works only in single mode. See
  [section 16](#16-keep-copy-rename-and-file-commands).

### Fullscreen

`F` toggles fullscreen. `Esc` leaves fullscreen, or minimizes the window when
it is not fullscreen.

### Closing a cell

Right-click, **Close**, or `Ctrl+F4`.

---

## 5. Playing, pausing and seeking

| To do this | Key or mouse |
| --- | --- |
| Play or pause one cell | Click it, or `Ctrl+Space` |
| Play or pause all cells | `Space` (also the Play/Pause media key) |
| Stop one cell | Right-click, **Stop** |
| Jump to 0%, 10% ... 90% | `0` ... `9` (all cells: `Alt+0` ... `Alt+9`) |
| Jump to a timecode | `T` opens a dialog (milliseconds allowed). All cells: `Shift+T` |
| Jump to a random position | `R` (all cells: `Shift+R`) |
| Step 1% back / forward | `Left` / `Right` |
| Step 10% back / forward | `;` / `'` |
| Step 5% | menu only: **Playback > Jump (to) > +5% / -5%** |
| Seek short / medium / long back | `Ctrl+Left` / `Ctrl+[` / `Ctrl+;` |
| Seek short / medium / long forward | `Ctrl+Right` / `Ctrl+]` / `Ctrl+'` |
| Next / previous frame | `S` / `D` (pauses the video) |
| Faster / slower / normal speed | `C` / `X` / `Z` |
| Seek with the mouse | Click or drag on the seek bar in the overlay |

Short, medium and long seeks are 5, 15 and 30 seconds by default (Settings,
Defaults, Playlist, Step Sizes; each 0.001 to 3600 seconds).

The mouse wheel over a cell changes volume, not position. To make the wheel
do something else, change it in the [Shortcuts editor](#21-shortcuts-editor).

**Initial state** (Settings, New Videos, Playback) decides whether new cells
start **Playing** (default), **Paused**, or **Stopped**. **Playback speed**
sets the starting speed (0.2 to 12, default 1.0).

**Reload** (`F5`, all cells `Shift+F5`) reopens the video in a cell. It is
useful after a network error.

---

## 6. Moving between files in a cell

A cell that plays a single local file can step through the other files of its
folder.

| Command | Keys |
| --- | --- |
| Play Next File | `N` or `PgDown` |
| Play Previous File | `B` or `PgUp` |
| Play Random File | `Shift+N` or `Shift+PgDown` |
| Back to Previous Random File | `Shift+B` or `Shift+PgUp` |

These are under **Playback** on the cell menu, and under **[ALL] > Playback**
for every cell.

### Order

Files are in natural name order ("Ep 2" before "Ep 10"). Next on the last file
wraps to the first.

### Include Subfolders

**Include Subfolders** is on by default (setting `video_defaults/dir_recursive`;
per cell on **Playback > Include Subfolders**; all cells under **[ALL] >
Playback > Include Subfolders**).

- **Off**: Next, Previous and Random stay in the playing file's own folder.
- **On**: the folder of the file playing when you turn it on becomes the
  cell's **root**. The cell walks everything under the root, depth first: a
  folder's own files first, then each subfolder in name order. Nothing above
  the root is used. If the playing file is in a subfolder when you turn it on,
  that subfolder becomes the root.

### Files to Play

**Playback > Files to Play** (per cell and for [ALL]; default from Settings,
New Videos, Playback, **Files to play**):

- **All Media**: videos, audio and pictures.
- **Videos Only** (default): videos only. Audio and pictures are skipped.
- **Images Only**: pictures only.

### Random play without repeats

**Play Random File** goes through every file once in random order before any
file repeats, and never starts a new round with the file that just played.
Each cell has its own order. New files join the current round. `Shift+B` goes
back through up to 1,000 earlier random picks. The order is not saved; it
lasts while the app is open.

**Skip files open in other cells** (on by default; Settings, Defaults,
Playlist, Folder Navigation) makes random play skip files that are already
open in another cell, when another file is available.

### What is skipped

- Hidden and system files and folders, when **Skip hidden and system files**
  is on (default).
- `$Recycle.Bin`, `System Volume Information`, `lost+found`, and NAS clutter
  (`@eaDir`, `#recycle`, `#snapshot`, `.Trash-*`).
- Junction loops.
- Missing files: up to 10 in a row are passed over, then the folder is scanned
  again.
- Files whose orientation does not fit the cell, when the cell's
  [Other orientation](#13-other-orientation-aspect-filter) is **Skip it**.

### Scan limit

**Scan limit** (default 50,000; 0 means no limit; maximum 1,000,000) caps how
many files and folders are looked at when a folder is read with its
subfolders. It counts everything, not only media, so that dropping a whole
drive by mistake does not hang the app.

---

## 7. Lists in a cell

A cell can play a **list**: a folder, an M3U/M3U8/PLS/XSPF playlist (a file or
a link), a YouTube playlist or channel page that yt-dlp reads, or an IPTV
channel list.

### Make and edit a list

- Dropping or adding a folder or a playlist file creates a list cell (with the
  default **Cells: One per item**).
- **List…** (`L`) opens the List window for the cell. On a cell that plays a
  single file, it first asks **Make this cell play a list?** with the choices
  **Just this video** or **Everything in its folder** (and **Include
  subfolders**).
- In the List window you can: add files, folders and links; paste; find on the
  list; sort (by name, length, date published, views, group, source order),
  reverse, randomize; move items to top or bottom; rename and remove items;
  copy titles, paths and links; show an item in its folder; get info (titles,
  lengths and thumbnails); play an item in this cell or open it in a new cell;
  open the whole list in a new cell; and export the list as an M3U file.
- **List view** (setting) shows titles, titles and paths, or paths.
  **Thumbnails when available** shows thumbnails, channel, views and upload
  date for lists from sites like YouTube. **Get info automatically** looks up
  titles, lengths and thumbnails for items you add; when off, use **Get Info**.

### Linked lists

A list that came from a folder, a file or a link can stay **linked** to its
source. A linked list updates from its source on the schedule in **Update
linked lists** (default **On playlist load**; other choices from every 5
minutes to every day), and each list can have its own schedule in its List
window. The window shows **New** and **Gone** counts after an update.
**Unlink** stops updates and keeps the current items.

### Lists in a saved playlist

Lists are saved inside the `.gpls` playlist. Several cells can play from one
list (for example, four cells on four channels of one IPTV list). **Grid >
Playlist Settings > Lists in Playlist…** shows every list with its source and
the cells that use it, and can duplicate, export, open in a new cell, remove,
or **Remove Unused**.

### At the end of the list, and failures

- **At the End of the List** (per cell; default from **When list ends**):
  **Start Over** (default), **Pause At Start**, **Stop**, **Close**.
- **When Video Fails** (list cells): **Play Next** (default) moves on after
  **Next after** seconds (default 2); **Show Error** stops on the error. Play
  next does not retry an item that is gone or refused.
- **Randomize List** (`Ctrl+Shift+N`) shuffles the cell's list once, with the
  playing item at the top. Next then plays straight down the new order.
- **Leave the List** returns the cell to plain folder stepping.
- **M3U size limit** (default 512 MB) stops very large list files from loading.
  IPTV lists can be hundreds of megabytes and take about 2.5 times their size
  in memory.
- Aspect ratio and crop given by an M3U channel list are applied to its
  channels unless you pick another.

---

## 8. Loops and When finished

### A-B loop

| Action | One cell | All cells |
| --- | --- | --- |
| Set Loop Start (A) | `[` | `Shift+[` |
| Set Loop End (B) | `]` | `Shift+]` |
| Loop Reset | `\` | `Shift+\` |

In Alabaster, `[` and `]` set loop points. (Upstream GridPlayer used them to
seek.) The loop range is drawn on the seek bar and saved with the playlist.

### Toggle Loop File (Shift+L)

`Shift+L` switches the cell to **Loop This File**. Pressing it again puts back
the **When finished** action the cell had before (for example Play next
file), and the overlay shows "Loop file: off (back to …)". If Loop This File
was chosen from the menu, so there is nothing to go back to, `Shift+L` only
reports "Loop file: on". Not offered for live streams.

### Loop Chapter

**Playback > Loop > Loop Chapter** sets the A-B loop to the chapter that is
playing. Shown when the video has chapters.

### Random Loop

**Playback > Loop > Random Loop** makes the cell start at a random position,
and jump to a random position each time it would loop back to the start. The
default for new cells is **Start at random position** (off).

### When finished

**Playback > When Finished** decides what happens at the end of a file:

| Choice | Result |
| --- | --- |
| **Loop This File** (default) | Start again. Loops are seamless, even for short clips. |
| **Play Next File** / **Play Previous File** | Go to the next or previous file of the folder or list. |
| **Play Random File** | Go to a random file (no repeats until all have played). |
| **Pause At Start** | Go back to the start and pause. |
| **Stop** | Stop. |
| **Close** | Close the cell. |

For a picture, When finished runs after the **Slide duration**.

---

## 9. Volume and audio

### Volume and mute

- **New cells start muted, at 0%**, so a full grid does not play every
  soundtrack at once. This is the **Muted** setting (Settings, New Videos,
  Audio), on by default. Turn it off to start cells with sound at **Volume**
  (default 100%).
- The mouse wheel over a cell (or **Audio > Increase / Decrease Volume**)
  changes that cell's volume by one step. The step is **3%** by default
  (setting **Volume step per wheel notch or key press**, 1 to 25%). A step of
  5% saved by an older version is moved to 3% once.
- `M` mutes every cell. If every cell is already muted, `M` unmutes them all.
  **[ALL] > Audio** has separate Mute and Unmute items.
- **Audio > Mute / Unmute** mutes one cell. It has no default key; you can give
  it one in the Shortcuts editor.
- **Mute is volume 0%.** No level is kept behind it. Unmuting, or turning up
  from 0%, goes to one step (3%), then 6%, and so on. Turning down to 0%
  mutes. Playlists saved with a muted cell open with it at 0%. If you want a
  mute that keeps your level, use the Windows or speaker mute.
- Volume goes from 0% to 100%.
- With **Disable mouse wheel events** on (Grid > Playlist Settings), the wheel
  over a cell does nothing; keys still work.

### Audio tracks, mode, delay and device

- **Audio > Audio Track** picks a track. The default for new cells is **Audio
  track: Default**; **Preferred Language** picks the first track that matches
  your **Languages** list; **Disable Audio** decodes no audio (not the same as
  muted).
- **Audio > Audio Mode**: Original, Stereo, Reverse Stereo, Left, Right, Dolby
  Surround, Headphones, Mono.
- **Audio > Audio Delay**: `K` makes audio later, `J` earlier (all cells:
  `Shift+K`, `Shift+J`); **Set Delay** types a value; **Reset** clears it.
- **Audio > Audio Device** sends one cell's sound to another output device.
- **Detect external audio files** (off by default) offers audio files next to
  the video with the same name in the Audio Track menu. They open only when
  you pick one.

### Audio files

Audio files play in a cell like videos, with an audio icon in place of a
picture. Folder stepping includes them only when Files to Play is **All
Media**.

---

## 10. Subtitles

- **Drag a subtitle file onto a cell** to attach it to that cell's video. The
  first dropped file is selected. You can also use the Subtitle Track menu to
  add external subtitle files.
- **Subtitles > Subtitle Track** picks a track or turns subtitles off.
- **Subtitles > Subtitle Delay**: `H` later, `G` earlier (all cells:
  `Shift+H`, `Shift+G`), **Set Delay**, **Reset**.
- Defaults for new cells (Settings, New Videos, Subtitles): **Subtitles**
  (Off by default; Preferred Language; Default), **Languages**, **Text
  encoding** for files that are not UTF-8 (UTF-8 is detected automatically),
  and **Detect external subtitle files** (offers same-named files next to the
  video).
- **Subtitle Style** (Settings, General): font, size (relative to VLC's size),
  color, bold, outline, shadow, background box, and **Raise from bottom**.
  Style applies to text subtitles; ASS and SSA keep their own style except
  the position.
- **Find subtitles on SubtitleCat.com…** appears on the Subtitles menu only
  when the optional SubtitleCat.com plugin is enabled. It is off by default.
  See [Plugins and streaming](PLUGINS-AND-STREAMING.md#subtitlecatcom-plugin).

---

## 11. Picture: zoom, view mode, aspect, crop, position

All of these are under **Video** on the cell menu and under **[ALL] > Video**.

### Zoom

- Zoom in: `.`, `+` or `Ctrl+Wheel-Up`. Zoom out: `,`, `-` or
  `Ctrl+Wheel-Down`. Reset: `/` or `*`. All cells: add `Shift`.
- **Zoom to Selection**, or `Ctrl+Drag` over the picture: draw a rectangle to
  zoom into. `Esc` cancels.
- **Zoom to Cursor** zooms toward the mouse pointer instead of the alignment
  point.
- Zoom step (default 10%) and **Proportional zoom** are in Step Sizes. Zoom
  goes up to 10x.

### Moving the picture

- `Middle-Drag` moves the picture inside its cell.
- `Alt+Left`, `Alt+Right`, `Alt+Up`, `Alt+Down` move it by steps.
- **Position > Set Position** types an offset in pixels. **Position Reset**
  clears it.
- **Position > Align …** sets which side keeps the picture when it is cut or
  has bars (Center, Top, Bottom, Left, Right, and the corners). Zoom goes
  about this point.
- **Move Past Edges** lets a moved or zoomed picture go past the cell edges as
  long as half stays in view.

### View mode

- **Fill** (default): covers the cell and cuts off the edges.
- **Fit**: shows the whole picture with bars.
- **Stretch**: covers the cell and changes the picture's shape.

### Aspect ratio

**Default** keeps the video's own shape (or the one its channel list gives),
or pick 16:9, 4:3, 1:1, 16:10, 2.21:1, 2.35:1, 2.39:1, 5:4. Videos with
non-square pixels (for example DVB channels) are shown in their real shape.

### Crop

- Presets: 16:10, 16:9, 4:3, 1.85:1, 2.21:1, 2.35:1, 2.39:1, 5:3, 5:4, 1:1.
- Margins: `U`/`I` left more/less, `O`/`P` top more/less, `Alt+U`/`Alt+I`
  right, `Alt+O`/`Alt+P` bottom. `Y` turns crop off.
- **Set Crop** opens a dialog with margins in pixels and a preview.

### Deinterlace

**Video > Deinterlace**: Automatic (only videos marked interlaced; default),
On, Off, and the mode (Auto, Discard, Blend, Mean, Bob, Linear, X, Yadif,
Yadif (2x), Phosphor, Film NTSC (IVTC)). With hardware decoding the GPU may use
another mode it supports.

### Video track

**Video > Video Track** picks a video track when a file has more than one.

---

## 12. Transforms and Rotate to fit

### Transform menu

**Video > Transform** on a cell: **Rotate 90**, **Rotate 180**, **Rotate
270**, **Flip Horizontally**, **Flip Vertically**, **Transpose**,
**Anti-transpose**, **No Transform**. The same items for every cell are
under **[ALL] > Video > Transform**. The default for new cells is Settings,
New Videos, Video, **Transform** (default none). A transform reopens the
video, because VLC applies it only when opening a file.

### Rotate to fit

**Rotate videos to fit their cells** (Settings, General, Player, Video and
sound; also **Video > Transform > Rotate Videos to Fit Cells** on the cell
menu) is an app-wide switch, **off by default**.

When it is on:

- A landscape video in a cell taller than wide is turned to stand up, and a
  portrait video in a cell wider than tall is turned to lie down, so more of
  the cell is picture.
- **Turn direction** chooses **Rotate 90 (clockwise)** (default) or **Rotate
  270 (counter-clockwise)**.
- The check runs when a file loads (including Next, Previous and Random), when
  a cell settles on a new shape after the grid or window is resized, and when
  you change the setting.
- A transform you pick from the menu wins for that file. The next file in the
  cell is turned to fit again.
- A video or cell within 5% of square is not turned.
- A video with an aspect ratio or crop shape picked for it (or given by its
  channel list) is not turned, because it is shown in that shape either way.
- Turning reopens the video, so the picture blinks once.

### Keys for transforms

The default keymap gives **no keys** to the transform commands or to Rotate to
fit. You can assign your own in the [Shortcuts editor](#21-shortcuts-editor).
A layout the maintainer uses:

| Key | Command (Shortcuts editor name) |
| --- | --- |
| `V` | Rotate 90 |
| `M` | Rotate 270 |
| `Shift+V` | No Transform |
| `Shift+M` | Rotate Videos to Fit Cells (turns Rotate to fit on or off) |

`V`, `Shift+V` and `Shift+M` are free in the default keymap. `M` is the
default key for **Mute / Unmute** of all cells. If you assign `M` to Rotate
270, the editor asks whether to reassign it, and all-cells mute then has no
key unless you give it another.

---

## 13. Other orientation (aspect filter)

**Playback > Other Orientation** decides what a cell does when Next, Previous,
Random or When finished, stepping through a folder, lands on a file whose
orientation (portrait or landscape) is not the cell's. A cell taller than wide
wants portrait files. It does not filter single-cell lists.

| Menu item | Setting name | Behavior |
| --- | --- | --- |
| **Off** | Play it (default) | Play whatever comes next. |
| **Skip Other Orientation** | Skip it | Pass over files of the other orientation. Up to 10 files are checked per step; after that the next file is taken whatever its shape. |
| **Ask on Other Orientation** | Ask | Pause and ask "Play anyway" or "Skip". |

- It applies only to moving on. The file already playing is never affected.
- It is set per cell, for all cells under **[ALL] > Playback > Other
  Orientation**, and as a default in Settings, New Videos, Playback, **Other
  orientation**. A saved playlist keeps each cell's choice.
- The cell's shape is measured live, so resizing the window or changing the
  grid can change what fits.
- A file whose shape cannot be read counts as fitting.
- File shapes are cached in `media_shapes.json` in the data folder.

!!! warning "Ask mode"
    **Skip it** is the supported mode. **Ask** exists, but it has not been
    re-verified recently. Treat it as experimental.

---

## 14. Pictures as slides

Pictures play as slides: each one shows for the cell's **Slide duration**,
then the cell's When finished action runs, as at the end of a video. An
animated GIF plays as VLC plays it.

- Supported: `jpg`, `jpeg`, `jpe`, `jfif`, `png`, `webp`, `gif`, `bmp`, `tif`,
  `tiff`.
- **Slide duration**: 1 to 3600 seconds, default 10. Per cell on
  **Playback > Slide Duration** (presets), default in Settings.
- To step through pictures in a folder, set **Files to Play** to **Images
  Only** or **All Media**. A picture you drop directly is always opened.

---

## 15. Chapters, bookmarks and SponsorBlock

### Chapters

**Playback > Chapters** appears when a video has chapters (from the file, or
YouTube chapters from yt-dlp): **Previous Chapter**, **Next Chapter**, and a
chapter list to jump to. **Loop Chapter** is under Loop.

### Bookmarks

**Playback > Bookmarks**: **Add Bookmark** at the current time, **Previous
Bookmark**, **Next Bookmark**, a list to jump to, and **Manage Bookmarks…**.
The manage window can rename, edit the time, move a bookmark to the current
position, remove, copy (with or without milliseconds), and paste timestamps
from text. Bookmarks show as marks on the seek bar.

**Share bookmarks between cells with the same file** (on by default): cells
playing the same file share its bookmarks, and they stay when a cell closes.
Off: each cell has its own, removed when the cell closes. **Grid > Playlist
Settings > Bookmarks in Playlist…** lists every bookmark in the playlist.

### SponsorBlock

For YouTube videos, Alabaster can look up segments that viewers marked on
[SponsorBlock](https://sponsor.ajay.app/) (sponsor, self-promotion,
interaction reminder, intro, outro, preview, hook, filler, non-music,
highlight) and either skip them or show them on the seek bar. It is off by
default (Settings, Streaming, SponsorBlock). Only a short prefix of a hash of
the video ID is sent. SponsorBlock data is CC BY-NC-SA 4.0.

---

## 16. Keep, copy, rename and file commands

### Keep (E)

`E` is **Keep**. It works only in **single mode**, on a cell playing a
**local file**.

1. It **copies** (never moves) the playing file into a sibling folder named
   after the file's folder with `_keep` added. For
   `D:\Clips\Cats\video.mp4` the copy goes to
   `D:\Clips\Cats_keep\video.mp4`. The folder is created if needed.
2. If a file with that name is already in the keep folder, nothing is copied.
3. Then the cell plays the next file, as `N` would.

Keep shows no message on screen. The result ("Keep: copied …", "exists,
skipped", or a failure) is written to `gridplayer.log`. Keep has no options
yet; choosing copy or move and turning Keep off are listed as
[future features](FUTURE.md).

`K` is **not** Keep. `K` is Audio Delay Later.

### Copy and file commands

| Command | Where | What it does |
| --- | --- | --- |
| **Copy File** | `Ctrl+C`, **File > Copy File** | Puts the file (or link) on the clipboard as a file, so you can paste it into an Explorer folder, a chat, another player, or Add from Clipboard. |
| **Copy File Name** / **Copy File Path** | **File** menu | Copies the name or full path as text. |
| **Show in Folder** | **File** menu | Opens Explorer with the file selected. |
| **Copy URL** / **Copy URL at Current Time** / **Open in Browser** | **URL** menu (links only) | Copies the link, or the link with the current time where the site supports it, or opens it in your browser. |
| **Copy Paths and URLs** | **[ALL]** menu | Copies every cell's file or link, one per line, in grid order. Add from Clipboard takes that list back. |

### Rename (F4): in-app title only

`F4` (**Rename**) opens a dialog to change the **title shown on the cell** and
the **overlay color**. It does **not** rename the file on disk. On a list
cell, the title belongs to the list item for every cell playing it.

Known problems: if the cell shows a full path, the edit looks like a path;
after Next, Previous or Random the old custom title can stay until a restart or
playlist load. F4 Rename is marked for removal before release unless a use is
found.

`F2` is unbound on purpose. It is reserved for a future rename on disk (see
[Future features](FUTURE.md)).

### Show full path

**Show full path in cell title** (Settings, Playlist, Overlay; off by default)
shows a local file's whole path on the cell, cut in the middle when narrow.

---

## 17. Screenshots

`Alt+S` saves the current frame of the active cell; `Shift+Alt+S` saves one per
cell.

- **Folder**: empty means `screenshots` in the data folder.
- **Format**: PNG (default) or JPG with **Quality** (default 90).
- **File name** template, default `%F_%P`:

| Code | Becomes |
| --- | --- |
| `%f` | video title with extension |
| `%F` | video title without extension |
| `%p` | position, without milliseconds |
| `%P` | position, with milliseconds |
| `%n` | counter, 4 digits |
| `%D` | date, `YYYY-MM-DD` |
| `%T` | date and time, `YYYY-MM-DD_HH-MM-SS` |
| `%tX` | `strftime` code `%X` of the current time |
| `%%` | a percent sign |

Characters Windows does not allow in names are replaced. If a name exists, a
number is added.

---

## 18. Sync between cells

- **Grid > Sync > Seek**: **Disabled** (default), **Sync By Percent** (seeking
  one cell seeks the others to the same share of their length), **Sync By
  Timecode** (to the same time).
- **Grid > Sync > Zoom and Position**: zooming or panning one cell does the
  same in the others.
- **Grid > Sync > Play / Pause** and **Speed**.
- **Sync Others** on a cell menu does it once: seek the others to this cell's
  percent or timecode, or copy this cell's zoom and position to them.

---

## 19. Saved playlists, per-cell profiles and snapshots

### Saved playlists (.gpls)

| Command | Key |
| --- | --- |
| Save Playlist | `Ctrl+S` |
| Save Playlist As | `Ctrl+Shift+S` |
| Open Playlist | `Ctrl+O` |
| Recent Playlists | menu |
| Close Playlist | `Ctrl+Shift+Q` |

A `.gpls` file is JSON. It holds the cells and each cell's settings (volume,
zoom, crop, tracks, loop points, transform, aspect filter and so on), the grid
layout, the window position when **Save window position and size** is on,
snapshots, bookmarks, lists, and per-cell profiles. Older text-format
GridPlayer playlists still open. Playlists written by Alabaster do not open in
GridPlayer 0.5.x or older.

Options (Settings, Defaults, Playlist, Saving / Restoring):

- **Save videos playback position** and **Save videos playback status**
  (off by default).
- **Save video paths relative to playlist file** (off): lets you move a
  playlist together with its videos.
- **Save all settings in the playlist** (off): writes every Playlist and New
  Videos value, so the playlist plays the same on another computer. Later
  changes to the defaults then no longer reach it.
- **Unsaved changes on close**: **Discard Changes** (default), **Ask**, **Auto
  Save or Discard**, **Auto Save or Ask**. Auto save works only for a playlist
  that already has a file. With the default, save before you close.
- **Reopen last playlist on startup** (off) and the Recent Playlists list
  (Settings, General, Player, History).
- The window title shows the playlist name.

**Grid > Playlist Settings > Edit Playlist Settings…** edits the open
playlist's own values. In Settings, a setting that the open playlist overrides
is marked "The open playlist has its own value."

### Per-cell profiles and stable cell ids

Every cell has a permanent id (a UUID) that is saved with the playlist. The
playlist's `cell_profiles` section stores extra per-cell options under that
id, so they stay with the right cell when cells are reordered, shuffled or the
playlist is reopened. Profiles of closed cells are dropped on save.

Today the only profile value the player reads is the cell's **Other
orientation** (aspect filter). Playlists saved by earlier Alabaster builds
keep it in the profile, and it wins until you choose another value from the
menu. The profile format also has fields for weighted sources, scaling
filters, deband, end action and loop; nothing in the app sets or reads them
yet.

### Snapshots

A snapshot stores the state of the grid in a slot, 0 to 9, saved with the
playlist.

| To do this | Keys |
| --- | --- |
| Save to slot 0-9 | `Ctrl+Alt+0` … `Ctrl+Alt+9` |
| Load slot 0-9 | `Ctrl+0` … `Ctrl+9` |
| Delete a slot | **Snapshots > Delete Snapshot** |

If cells were closed since the snapshot was saved, it is applied to the cells
still there and a warning says "Snapshot applied to N of M cells".

---

## 20. Streaming links

Paste or drop a web link and Alabaster resolves it with the bundled yt-dlp (or
Streamlink, or opens it directly) and plays it in VLC. This section is a
summary; the full explanation is in
[Plugins and streaming](PLUGINS-AND-STREAMING.md).

- **Stream Quality** on the cell menu (for links with several qualities):
  **Auto (fit to pane)**, **Best** (default), **Audio Only**, or a resolution.
  Auto changes quality when the cell keeps a new size for **Adapt after**
  seconds (default 15).
- **Audio Track** switches language on multi-language streams.
- **On Network Error**: **Show Error**, **Reload a Few Times** (default, 3
  attempts), **Keep Reloading**.
- **Auto Reload** (live streams): reload every N minutes; 0 means never.
- **Video initialization timeout** (default 120 s): how long a video may take
  to open before an error shows.
- yt-dlp reads cookies from the browser you choose on Settings, Streaming,
  Cookies. Nothing is stored.

---

## 21. Shortcuts editor

Open it from the right-click menu, **Shortcuts**, or Settings (`F6`), page
**Shortcuts**.

- The tree groups commands as **Single video**, **All videos**, **Playlist**
  and **Program**, the same as the menus. **Mouse drag** entries (move video,
  pan, zoom to selection) and the drop-switch key are listed too.
- Filter by action name or shortcut, or show **Only changed**.
- **Add keyboard shortcut**, **Add mouse shortcut** (clicks, wheel, side
  buttons) and **Add mouse drag** append to a command's list. **Clear
  shortcut** removes one; **Reset shortcut** restores the default;
  **Reset all** restores every default.
- One shortcut cannot belong to two commands. If you pick one in use, the
  editor shows where and asks **Reassign**.
- Changes are stored in `settings.ini` as differences from the default keymap
  (`player/keymap`).

### Mouse side buttons

The mouse **Back** and **Forward** buttons (and extra buttons) can be assigned
like keys (`Back-Click`, `Forward-Click`, `Click-4`, `Click-5`). They have no
default command. Side buttons keep working when **Disable mouse click
events** is on, because they act as keys, not clicks on the picture.

---

## 22. Settings window

`F6`, or right-click, **Settings**. Pages:

- **General**: Player, Subtitle Style, Shortcuts, Language.
- **Defaults**: Playlist, New Videos.
- **Streaming**: Link Resolution, SponsorBlock, Cookies, Network.
- **Plugins**: SubtitleCat.com.
- **Advanced**: Video Decoder, Logging.

The window has search, a reset per page, and an **Open data folder** button.
**Test a YouTube link** (Link Resolution) and **Test network** (Network) run
checks and can copy a report.

Settings on the New Videos page are defaults for **new** cells. A cell copies
them when it is created and keeps its own values after that. Changing a
default does not change cells that already exist.

The **Language** page is inherited from upstream. Alabaster adds new text in
English only and does not maintain translations; strings added by Alabaster
appear in English whatever language you pick.

Every setting, with its default and range, is in
[Settings](reference/settings.md).

---

## 23. Window, tray, media keys and screensaver

Settings, General, Player:

- **Color scheme**: System (follows Windows), Light, Dark.
- **Stay on top** (restart needed), **Start with maximized window**, **Start
  in fullscreen mode**.
- **Disable screensaver while playing** (on).
- **Control playback with media keys globally** (on): media keys work while
  another window has focus. Alabaster also shows in the Windows media
  controls.
- **Tray**: **Show icon in the tray**, then **Minimize to the tray**, **Close
  to the tray**, **Hide from the taskbar**, and **Stop video decoding while in
  the tray** (audio keeps playing).
- **Pause videos when minimized** (Grid > Playlist Settings, on by default).
- **Minimize** is on the program menu; **Quit** is `Q`.

---

## 24. Single instance and opening files from Explorer

- **Allow only one instance** (on by default). Opening files while Alabaster is
  running sends them to the running window instead of starting a second one.
  The hand-off uses the pipe `\\.\pipe\gridplayer-alabaster-fileopen` with a
  JSON message (the old pickle format is refused).
- When you select several files and folders in Explorer and choose Open with
  Alabaster, Explorer starts one copy per item. Each copy hands its item to
  the first window, so everything lands in **one window**: a cell per file and
  a cell per folder (folders play as lists). Cells arrive in the order the
  hand-offs reach the window, which may not be Explorer's order.
- A `.gpls` playlist opened this way replaces the grid; it is not added.

---

## 25. Video decoder and performance

Settings, Advanced, Video Decoder:

| Decoder | Meaning |
| --- | --- |
| **Hardware** (default) | GPU decoding, videos spread over VLC processes. |
| **Hardware SP** | GPU decoding inside the player's own process. Not recommended for more than 4-6 videos. |
| **Software** | CPU decoding in VLC processes. High CPU with high resolutions. |
| **Software SP** | CPU decoding inside the player's process. |
| **Dummy** | Plays nothing (for testing). |

- **Videos per process** (default 4, 1-64): how many videos share one VLC
  process in Hardware or Software mode. Too high can freeze the app. If panes
  turn grey when you press Next in a grid, try 1.
- **VLC Options**: extra VLC command-line options for every video, for
  example `--network-caching=1000`. Options that open a server, stream out, or
  turn on Lua are dropped. Videos reload when changed.
- **Experimental**: **Opaque overlay (fix black screen)**, **Fake overlay
  invisibility**, **Force native drag-n-drop**, **HW video border fix** (crops
  a few pixels to hide edge glitches; Auto by default).
- **Cache** (General, Player): thumbnails and downloaded lists on disk (up to
  1024 MB by default) or in memory.
- **Logging** (Advanced): log level for the app and for VLC, and an optional
  size limit with rotated files.

---

## 26. Troubleshooting

| Problem | What to try |
| --- | --- |
| No sound | New cells start muted. Scroll up over the cell, or turn off **Muted** in Settings, New Videos, Audio. |
| Keys do nothing | Move the mouse over a cell. Keys act on the cell under the pointer. |
| A playlist shuffles every time it opens | Untick **Grid > Shuffle On Load** and save the playlist again. |
| Audio files or pictures in a dropped folder are missing | **Files to play** is Videos only by default. Pick All Media. |
| Next or Random skips files | **Other orientation** may be Skip it. For Random only, **Skip files open in other cells** passes over files already open in another cell. |
| `E` does nothing | Keep works only in single mode on a local file. Check `gridplayer.log`. |
| YouTube says "Sign in to confirm you're not a bot" | Choose your browser on Settings, Streaming, Cookies and make sure you are signed in there. See [cookies](PLUGINS-AND-STREAMING.md#browser-cookies). |
| YouTube links fail | Install Deno and restart. Run **Test a YouTube link**. |
| Panes go grey or stutter with many videos | Set **Videos per process** to 1, or try Hardware SP. Two hardware players on one integrated GPU compete; see [Known limitations](KNOWN-LIMITATIONS.md). |
| Black cells | Turn on **Opaque overlay (fix black screen)**. |
| A typed `gridplayer` starts another version | That is upstream GridPlayer on your PATH. Run Alabaster's own executable. |
| Where is the log? | `gridplayer.log` in the data folder (**Open data folder** in Settings). |

Report problems in the
[Alabaster repository's issues](https://github.com/XDevMatt/alabaster-gridplayer/issues),
not upstream GridPlayer's.
