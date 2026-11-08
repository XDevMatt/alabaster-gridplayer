# Window, tray and command line

## Window

| Do | Key or menu |
| --- | --- |
| Fullscreen | `F` |
| Leave fullscreen, or minimize | `Esc` |
| Minimize | right-click, **Minimize** |
| Settings | `F6` |
| About | `F1` |
| Quit | `Q` |
| Next / previous active cell | `Tab` / `Shift+Tab` |

Settings, General, Player:

- **Color scheme**: System (default), Light, Dark.
- **Allow only one instance** (on): opening a file while Alabaster runs
  sends it to the running window. Alabaster's channel is its own, so an
  upstream GridPlayer running alongside isn't affected.
- **Stay on top** (takes effect after a restart), **Start with maximized
  window**, **Start in fullscreen mode**.
- **Disable screensaver while playing** (on).
- **Control playback with media keys globally** (on): Play/Pause, Stop,
  Next and Previous media keys work even when the window isn't focused.
  **Media Next** / **Media Previous** switch the cell shown in Single Mode.
- **History**: the recent lists for files and playlists, their size, and
  **Reopen last playlist on startup** (off).

Defaults, Playlist, Playback: **Pause videos when minimized** (on) and
**Pause background videos on single mode** (on).

## Tray

Settings, General, Player, Tray (all off by default): **Show icon in the
tray**, then **Minimize to the tray**, **Close to the tray**, **Hide from the
taskbar**, and **Stop video decoding while in the tray** (sound keeps
playing).

## Video decoder

Settings, Advanced, Video Decoder:

- **Hardware** (default) decodes on the GPU; **Software** on the CPU.
- Both spread videos over separate VLC processes, **Videos per process** at a
  time (default 4). Too many per process can freeze the app.
- **Hardware SP** / **Software SP** play every video in Alabaster's own
  process. Fine for a few cells; not recommended past 4 to 6.
- **VLC Options**: extra VLC command-line options for every video, such as
  `--network-caching=1000`. Options that open a server, stream out or turn on
  Lua are dropped. Videos reload when you change it.
- **HW video border fix** crops a few pixels off the edges to hide hardware
  video glitches.

## Command line

```powershell
GridPlayer.exe [options] [FILE|URL ...]
```

Anything that isn't an option opens on startup: media files, folders,
`.gpls` playlists, media lists (`.m3u`, `.m3u8`, `.pls`, `.xspf`) or links.
A folder or a media list plays in one cell. Put `--` before file names that
start with a dash.

| Option | Does |
| --- | --- |
| `--user-data-dir PATH` | Keep settings and logs in `PATH`. Relative paths are from the current folder. Same as the `GP_USER_DATA_DIR` environment variable; the option wins. |
| `--version` | Show the version and exit. |
| `--help` | Show the options and exit. |

See [Data folder and portable mode](../reference/data-folder.md).

## Logs

Settings, Advanced, Logging: **Log level** (Warning by default), a separate
level for VLC (None by default), and **Limit log file size** with how many
old logs to keep. The log is `gridplayer.log` in the data folder.
