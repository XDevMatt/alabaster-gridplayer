# Milestone

Read this first after a memory wipe. Sysop is the person driving this
fork. Call them sysop. The tree is frozen for QC. Do not start the
deferred work in `docs/after-qc.md`, and do not start the cell-layout
work below, until sysop says QC is done.

Last recorded head: `3cf651c` (shallow clone, depth 1). Nothing here
has been committed. Do not commit or push unless sysop asks.

## How to launch

From the repo:

```powershell
uv run gridplayer
```

From `.venv\Scripts`, PowerShell does not search the current folder.
The leading `.\` is required:

```powershell
.\gridplayer.exe
```

Bare `gridplayer` starts the system install,
`C:\Users\<user>\AppData\Local\Programs\Python\Python312\Scripts\gridplayer.exe`,
GridPlayer 0.5.3. That copy imports `PydanticValueError` and crashes
on pydantic 2. This fork does not. Leave that install alone.

## Done, and the decisions that must stay

### Browser cookies are a yt-dlp flag, not a file

`cookies/from_browser` and `cookies/browser_profile` in
`gridplayer/settings.py`. Empty browser means the flag is not passed.
A name becomes YoutubeDL `cookiesfrombrowser` of
`(name, profile or None, None, None)`, the same as
`yt-dlp --cookies-from-browser firefox "URL"`. Nothing from the
browser is written into `cookies.txt`.

When a browser is selected, refresh-merge back into the stored jar is
skipped, even if a stored jar is also passed to that one YoutubeDL
call. The stored-cookie file and paste import stay as their own
feature. Do not bring back an "import browser cookies into the jar"
button. Deleted on purpose: `gridplayer/utils/browser_cookies.py`,
`gridplayer/dialogs/browser_cookies.py`, `tests/test_browser_cookies.py`.

Wired through `gridplayer/utils/cookies.py` (`browser_cookie_opts`,
`ytdl_cookies`) and the YouTube checkup. Streamlink still receives
only the stored jar. SponsorBlock and the "is this URL handled" check
do not get cookies.

The Cookies page controls are in `resources/ui/settings_dialog.ui`
and the generated `gridplayer/dialogs/settings_dialog_ui.py`. Edit the
`.ui`, then regenerate. Do not regenerate from an older `.ui` and drop
the browser row.

### Shortcuts is on the right-click menu

Program menu, the line under Settings. Action id `Shortcuts`, func
`shortcuts`, no default key. `SettingsManager.cmd_shortcuts` opens
`SettingsDialog` with `page="page_general_shortcuts"`. Settings (F6)
still opens on Player.

Each command already holds a list of shortcuts. Add keyboard shortcut
and Add mouse shortcut append. The old binding stays until it is
removed. One shortcut cannot belong to two commands. Assigning it
takes it off the other.

Next Video, Previous Video, Play Next File, Play Previous File,
Reload, and Reload [ALL] are already in that tree. A-B loop is
already on keys: `,` start, `.` end, `/` clear. Loop This File is
only a When Finished menu choice and has no key. Binding that row
only turns the mode on. It does not restore the cell's previous end
action.

## Tests already run

Cookie and settings subset, after the flag work: 116 passed
(`test_cookies_applied.py`, `test_settings_cookies.py`,
`test_ytdlp_checkup.py`, `test_settings.py`).

Shortcut exposure: 105 passed
(`test_settings_sections.py`, `test_menu.py`, `test_managers_settings.py`,
`test_pan.py`, `test_zoom_select.py`).

The full suite has not been run. This is a Qt desktop app. There is
no browser pass to do.

## Dirty files

Modified against `3cf651c`:

- `AGENTS.md`
- `gridplayer/dialogs/settings.py`
- `gridplayer/dialogs/settings_dialog_ui.py`
- `gridplayer/params/actions.py`
- `gridplayer/params/menu.py`
- `gridplayer/player/managers/settings.py`
- `gridplayer/settings.py`
- `gridplayer/utils/cookies.py`
- `gridplayer/utils/ytdlp_checkup.py`
- `resources/ui/settings_dialog.ui`
- `tests/test_cookies_applied.py`
- `tests/test_managers_settings.py`
- `tests/test_menu.py`
- `tests/test_settings_cookies.py`
- `tests/test_settings_sections.py`
- `tests/test_ytdlp_checkup.py`

Untracked: `docs/` (the after-QC spec) and this file.

## After QC, in this order

Sysop has not ranked these against each other beyond "after QC". The
picture and loop spec is `docs/after-qc.md`. The layout was agreed
earlier and is not in that file.

1. One key that toggles a cell between Loop This File and that cell's
   own When Finished action (next file, shuffle from the original
   folder, or whichever end action it had). Per cell. Remember the
   replaced action and save it with the video. A-B marks stay in
   charge while they are set. A cycling `l` for A-B is optional
   because `,` `.` `/` already exist. Proposed default for the toggle
   is `Shift+L`.
2. Video Decoder page: a banding filter (`gradfun`, off by default)
   and separate upscale and downscale algorithms. 100% means one
   source pixel to one pane pixel, not view scale 1.0. Scale 1.0 means
   fit the cell. Hardware ignores `--swscale-mode`. Details, including
   the transform-filter clash, are in `docs/after-qc.md`.
3. Dynamic cell layout from aspect, not resolution, and not stretch.
   Two cell types only. Portrait videos are full-height stripes.
   Landscape videos are rectangles. After a cell's aspect changes
   (Play Random File / `VideoEndAction.SHUFFLE_FILE` picks the next
   file from that cell's original folder), reallocate and place them.
   Example for four cells with two portraits and two landscapes: full
   height stripes on the left and right edges, two stacked rectangles
   in the middle. Today every row and column stretch is 1
   (`GridManager._adjust_grid_stretch`), so a portrait sits in a thin
   band inside an equal rectangle. Do not replace the two cell types
   with a resolution-weighted pack.

## Decoder page, as it is now

Settings, Advanced, Video Decoder. Hardware is the Windows default.
Software draws from memory. SP runs every video in the app process.
Without SP, videos share VLC processes, and Videos per process
(default 4, max 64) is the group size. macOS forces Hardware SP.
VLC Options is free text, appended last, and reopens videos. Opaque
overlay, fake overlay invisibility, and the driver choice also reopen
videos. HW video border fix applies on the next draw. For this QC,
leave Hardware unless a cell stays black (opaque overlay) or the
hardware edge is dirty (border fix).
