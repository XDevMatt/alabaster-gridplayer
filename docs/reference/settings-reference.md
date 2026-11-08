# GridPlayer Alabaster settings reference

This page lists every setting in the Settings dialog. For each one it gives the default value and where the value is kept.

It was checked against the code on master (Alabaster, a fork of GridPlayer 0.5.5) on 2026-10-30.

## Where settings are kept

Alabaster keeps settings in three kinds of place.

### 1. Global settings file

- This is a plain INI file named `settings.ini`. It is written with Qt QSettings in INI format, not in the registry.
- Normal install on Windows: `%APPDATA%\vzhd1701\GridPlayer-Alabaster\settings.ini`
  (for example `C:\Users\<you>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster\settings.ini`).
- The folder is Alabaster's own. Upstream GridPlayer uses `%APPDATA%\vzhd1701\GridPlayer`, so the two do not share settings.
- Portable build: if a folder named `portable_data` sits next to the exe, everything goes there instead.
- `--user-data-dir <folder>` on the command line, or the `GP_USER_DATA_DIR` environment variable, moves it to that folder. This wins over portable mode.
- Clicking OK in the Settings dialog writes the values to this file. A key that was never saved uses the built-in default.
- These files are in the same folder: `gridplayer.log` (the log), `screenshots\` (the default screenshot folder), and `media_shapes.json` (a cache of video shapes).
- The thumbnail cache uses the system cache folder (`%LOCALAPPDATA%\vzhd1701\GridPlayer-Alabaster\cache`). In portable mode, or when the data folder was moved, it is `cache\` inside the data folder.

### 2. Saved playlist (`.gpls` file)

- A playlist is a JSON file with the `.gpls` extension. It is only written when you save the playlist.
- **Playlist (whole grid):** the `settings` object at the top of the file. It holds this playlist's own values for the *Playlist* and *New Videos* defaults pages. It also holds the grid layout (`grid_state`), the window position (`window_state`), and snapshots.
  - Normally only values that differ for this playlist are saved. That means values changed in the Playlist window, or from menus while the playlist is open, such as grid mode, single mode, or overlay off. Everything else follows the global file.
  - If **Save all settings in the playlist** is on, every Playlist and New Videos value is written. The playlist then stops following later changes to the global defaults.
- **Playlist (per cell):** the `videos` array has one entry per cell. Each entry holds that cell's own copy of every New Videos value, plus volume, zoom, crop, tracks, loop points, position, and so on. The `cell_profiles` object holds Alabaster's extra per-cell options, keyed by the cell id.
- **Playlist root lists:** the `bookmarks` and `lists` arrays are at the top of the file, next to `videos`. Bookmarks are per file. Lists are media lists such as M3U, folder, or channel lists.

### 3. Windows registry

- Alabaster does **not** save any setting in the registry.
- It only *reads* two registry values. It reads `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme` when Color scheme is System. It also looks up where VLC is installed.

### Other places

- `recent_list_videos`, `recent_list_playlists`, `last_playlist` and `player/tray_note_shown` are in `settings.ini`. They are not shown in the dialog.
- `migrations/volume_step_3` is a one-time marker in `settings.ini`. It is not a setting.
- Cookies are read from your browser when a link is opened and are never saved. An old `cookies.txt` in the data folder is ignored.

## How a cell gets its values

1. A new cell takes the playlist's own value if the playlist has one. Otherwise it takes the global value from `settings.ini`.
2. After that the cell has its own copy. Changing the global default later does not change cells that already exist.
3. The cell's copy is saved only in the playlist, under `videos`. With no saved playlist, closing the app loses it. The next cells start from the defaults again.

## Saved only in the playlist (per cell)

These have no global setting, or they differ from it per cell. Without a saved playlist they reset.

- Everything you change on one cell from its menu: volume, mute, zoom, view mode, aspect ratio, crop, alignment and shift, transform (rotate or flip), deinterlace, speed, end action, overlay color.
- Playback position (only when **Save videos playback position** is on). Playing or paused (only when **Save videos playback status** is on).
- A-B loop points (`loop_start`, `loop_end`).
- Chosen audio track, subtitle track, video track, audio device, audio delay and subtitle delay.
- External audio and subtitle files added to the cell.
- The cell title, and the list it plays plus its position in that list.
- Grid placement: row, column and span of each cell (`grid_state.cells`, `video_order`).
- Cell profile (`cell_profiles`): **aspect filter** (skip or ask about files of the other orientation), upscale and downscale filters, deband, the cell's own end action and loop, and weighted sources.
- At the playlist root: bookmarks, media lists, and snapshots.

## Settings by page

Key = the name in `settings.ini` (section/name). Where:
- **Global** = `settings.ini` only.
- **Global + Playlist (whole grid)** = global default, which a saved playlist can override.
- **Global + Playlist (whole grid) + Playlist (per cell)** = as above, and each cell also keeps its own copy.

### General > Player

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Color scheme | player/color_scheme | System | Global | System follows the Windows light or dark setting. |
| Allow only one instance | player/one_instance | On | Global | |
| Stay on top | player/stay_on_top | Off | Global | Hidden on Linux. |
| Start with maximized window | player/start_maximized | Off | Global | |
| Start in fullscreen mode | player/start_fullscreen | Off | Global | |
| Disable screensaver while playing | player/inhibit_screensaver | On | Global | |
| Control playback with media keys globally | player/media_keys_background | On | Global | |
| Rotate videos to fit their cells | player/auto_rotate | Off | Global | Alabaster. |
| Turn direction | player/auto_rotate_direction | Rotate 90 (clockwise) | Global | |
| Volume step per wheel notch or key press | player/volume_step | 3 (%) | Global | Was 5. A saved 5 is reset once to the new default. |
| Show icon in the tray | player/tray_icon | Off | Global | |
| Minimize to the tray | player/minimize_to_tray | Off | Global | Needs tray icon. |
| Close to the tray | player/close_to_tray | Off | Global | Needs tray icon. |
| Hide from the taskbar | player/hide_taskbar | Off | Global | Needs tray icon. |
| Stop video decoding while in the tray | player/tray_stop_video | Off | Global | Needs tray icon. |
| Enable recent list | player/recent_list_enabled | On | Global | The lists are kept in `recent_list_videos` and `recent_list_playlists`. |
| Maximum size | player/recent_list_max_size | 10 | Global | |
| Reopen last playlist on startup | player/reopen_last_playlist | Off | Global | Uses `last_playlist`. |
| Video initialization timeout | player/video_init_timeout | 120 (s) | Global | |
| Hide mouse after timeout | misc/mouse_hide | On | Global | |
| Timeout | misc/mouse_hide_timeout | 5 (s) | Global | |
| M3U size limit | player/list_max_mb | 512 (MB) | Global | |
| Keep (cache) | cache/mode | On disk | Global | |
| Limit (cache) | cache/max_mb | 1024 (MB) | Global | |
| Folder (screenshots) | screenshots/dir | empty | Global | Empty means `screenshots` in the data folder. |
| File name | screenshots/filename_template | %F_%P | Global | mpv-style template. |
| Format | screenshots/format | PNG | Global | |
| Quality | screenshots/jpg_quality | 90 | Global | JPG only. |

### General > Subtitle Style

Applies to text subtitles. VLC sets this per process, so it is global only.

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Font | subtitles/font | Default | Global | |
| Size | subtitles/size_scale | 100 (%) | Global | |
| Color | subtitles/color | #ffffff | Global | |
| Bold | subtitles/bold | Off | Global | |
| Outline | subtitles/outline | Normal | Global | |
| Color (outline) | subtitles/outline_color | #000000 | Global | |
| Shadow | subtitles/shadow | On | Global | |
| Color (shadow) | subtitles/shadow_color | #000000 | Global | |
| Background box | subtitles/background | Off | Global | |
| Color (background) | subtitles/background_color | #000000 | Global | |
| Raise from bottom | subtitles/margin | 0 | Global | |

### General > Shortcuts and Language

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Shortcuts page | player/keymap | no overrides | Global | Only the changed shortcuts are saved. |
| Language page | player/language | System language | Global | For example en_US. |

### Defaults > Playlist

These are the defaults for every playlist. The Playlist window shows the same page for the open playlist. A value set there is saved in that playlist's `settings` object.

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Save all settings in the playlist | playlist/save_all_settings | Off | Global + Playlist (whole grid) | On: every value on this page and on New Videos goes into the file. |
| Unsaved changes on close | playlist/unsaved_changes | Discard Changes | Global + Playlist (whole grid) | Never asks by default. |
| Save window position and size | playlist/save_window | Off | Global + Playlist (whole grid) | Saves `window_state`. |
| Save videos playback position | playlist/save_position | Off | Global + Playlist (whole grid) | Off: per-cell position is left out of the file. |
| Save videos playback status | playlist/save_state | Off | Global + Playlist (whole grid) | Off: playing or paused is left out. |
| Save video paths relative to playlist file | playlist/save_paths_relative | Off | Global + Playlist (whole grid) | |
| Pause background videos on single mode | playlist/pause_background_videos | On | Global + Playlist (whole grid) | |
| Pause videos when minimized | playlist/pause_minimized | On | Global + Playlist (whole grid) | |
| Share bookmarks between cells with the same file | playlist/bookmarks_shared | On | Global + Playlist (whole grid) | |
| Short seek | playlist/seek_step_short | 5.0 (s) | Global + Playlist (whole grid) | |
| Medium seek | playlist/seek_step_medium | 15.0 (s) | Global + Playlist (whole grid) | |
| Long seek | playlist/seek_step_long | 30.0 (s) | Global + Playlist (whole grid) | |
| Zoom | playlist/zoom_step | 10 (%) | Global + Playlist (whole grid) | |
| Proportional zoom | playlist/zoom_proportional | Off | Global + Playlist (whole grid) | |
| Skip hidden and system files | playlist/folder_skip_hidden | On | Global + Playlist (whole grid) | |
| Scan limit | playlist/folder_max_entries | 50000 | Global + Playlist (whole grid) | |
| Skip files open in other cells | playlist/shuffle_avoid_open | On | Global + Playlist (whole grid) | |
| Seek sync mode | playlist/seek_sync_mode | Disabled | Global + Playlist (whole grid) | |
| Sync zoom and position | playlist/view_sync | Off | Global + Playlist (whole grid) | |
| Sync play and pause | playlist/pause_sync | Off | Global + Playlist (whole grid) | |
| Sync speed | playlist/rate_sync | Off | Global + Playlist (whole grid) | |
| Disable mouse click events | playlist/disable_mouse_click_events | Off | Global + Playlist (whole grid) | |
| Disable mouse wheel events | playlist/disable_mouse_wheel_events | Off | Global + Playlist (whole grid) | |
| Disable overlay | playlist/disable_overlay | Off | Global + Playlist (whole grid) | The menu toggle sets the playlist value. |
| Show overlay border for active video | playlist/show_overlay_border | On | Global + Playlist (whole grid) | |
| Show full path in cell title | playlist/show_full_path_title | Off | Global + Playlist (whole grid) | |
| Hide overlay after timeout | playlist/overlay_hide_on_timeout | On | Global + Playlist (whole grid) | |
| Overlay timeout | playlist/overlay_timeout | 3 (s) | Global + Playlist (whole grid) | |
| Shuffle on load | playlist/shuffle_on_load | Off | Global + Playlist (whole grid) | |
| Grid mode | playlist/grid_mode | Auto (Rows First) | Global + Playlist (whole grid) | Saved in `grid_state` as `mode`. |
| Grid size | playlist/grid_size | 0 (auto) | Global + Playlist (whole grid) | `grid_state.size`. |
| Fit grid cells | playlist/grid_fit | On | Global + Playlist (whole grid) | `grid_state.is_fit`. |
| Rows | playlist/grid_rows | 3 | Global + Playlist (whole grid) | `grid_state.rows`. |
| Columns | playlist/grid_cols | 3 | Global + Playlist (whole grid) | `grid_state.cols`. |
| Show all cells even when empty | playlist/grid_preallocate | Off | Global + Playlist (whole grid) | `grid_state.preallocate`. |
| In-window drag | playlist/drop_action_internal | Move / Swap | Global + Playlist (whole grid) | |
| File drop | playlist/drop_action_external | Add | Global + Playlist (whole grid) | |
| Cells | playlist/add_mode | One per item | Global + Playlist (whole grid) | |
| Warn about too many cells | playlist/warn_many_cells | On | Global + Playlist (whole grid) | "Do not warn again" in the warning turns it off. |
| Warn above | playlist/many_cells_count | 12 | Global + Playlist (whole grid) | |
| List view | playlist/list_view | Titles | Global + Playlist (whole grid) | |
| Thumbnails when available | playlist/list_thumbnails | On | Global + Playlist (whole grid) | |
| Get info automatically | playlist/list_get_info | Off | Global + Playlist (whole grid) | |
| Update linked lists | playlist/list_update | On playlist load | Global + Playlist (whole grid) | A list can also set its own (`lists[].update`). |

### Defaults > New Videos

These are the starting values for new cells. A playlist can override them in `settings.video_defaults`. Each cell then keeps its own copy in `videos[]`, under the field name shown in the note.

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Overlay color | video_defaults/color | #ffffff | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `color`. |
| Audio track | video_defaults/audio_track_mode | Default | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `audio_selection`. |
| Languages (audio) | video_defaults/audio_languages | empty | Global + Playlist (whole grid) + Playlist (per cell) | |
| Detect external audio files | video_defaults/external_audio_autodiscover | Off | Global + Playlist (whole grid) + Playlist (per cell) | |
| Audio mode | video_defaults/audio_mode | Original | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `audio_channel_mode`. |
| Volume | video_defaults/volume | 1.0 (100%) | Global + Playlist (whole grid) + Playlist (per cell) | |
| Muted | video_defaults/muted | On | Global + Playlist (whole grid) + Playlist (per cell) | New cells start muted. Cell: `is_muted`. |
| Subtitles | video_defaults/subtitle_track_mode | Off | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `subtitle_selection`. |
| Languages (subtitles) | video_defaults/subtitle_languages | empty | Global + Playlist (whole grid) + Playlist (per cell) | |
| Text encoding | video_defaults/subtitle_encoding | Default | Global + Playlist (whole grid) + Playlist (per cell) | |
| Detect external subtitle files | video_defaults/external_subtitle_autodiscover | Off | Global + Playlist (whole grid) + Playlist (per cell) | |
| Zoom | video_defaults/scale | 1.0 | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `scale`. |
| Zoom to cursor | video_defaults/zoom_to_cursor | Off | Global + Playlist (whole grid) + Playlist (per cell) | |
| View mode | video_defaults/cell_view_mode | Fill | Global + Playlist (whole grid) + Playlist (per cell) | |
| Aspect ratio | video_defaults/aspect_ratio | Default | Global + Playlist (whole grid) + Playlist (per cell) | |
| Crop | video_defaults/crop_ratio | Margins | Global + Playlist (whole grid) + Playlist (per cell) | |
| Margins | video_defaults/crop | 0, 0, 0, 0 | Global + Playlist (whole grid) + Playlist (per cell) | |
| Alignment | video_defaults/anchor | Center | Global + Playlist (whole grid) + Playlist (per cell) | |
| Allow moving past the edges | video_defaults/shift_past_edges | Off | Global + Playlist (whole grid) + Playlist (per cell) | |
| Transform | video_defaults/transform | No Transform | Global + Playlist (whole grid) + Playlist (per cell) | Rotate to fit can change it per cell. |
| Deinterlace | video_defaults/deinterlace | Automatic | Global + Playlist (whole grid) + Playlist (per cell) | |
| Mode (deinterlace) | video_defaults/deinterlace_mode | Auto | Global + Playlist (whole grid) + Playlist (per cell) | |
| When finished | video_defaults/end_action | Loop this file | Global + Playlist (whole grid) + Playlist (per cell) | A cell profile can also set its own. |
| Include subfolders | video_defaults/dir_recursive | On | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `is_dir_recursive`. |
| Other orientation | video_defaults/aspect_filter | Play it | Global + Playlist (whole grid) + Playlist (per cell) | Play it, Skip it, or Ask (experimental). |
| Files to play | video_defaults/media_kind | Videos only | Global + Playlist (whole grid) + Playlist (per cell) | All media, Videos only, Images only. Applies to folders and stepping. |
| Slide duration | video_defaults/slide_duration | 10 (s) | Global + Playlist (whole grid) + Playlist (per cell) | 1 to 3600. Cell: `slide_duration_sec`. |
| When list ends | video_defaults/list_end_action | Start over | Global + Playlist (whole grid) + Playlist (per cell) | |
| When video fails | video_defaults/list_fail_action | Play next | Global + Playlist (whole grid) + Playlist (per cell) | |
| Next after | video_defaults/list_fail_wait | 2 (s) | Global + Playlist (whole grid) + Playlist (per cell) | |
| Start at random position | video_defaults/random_loop | Off | Global + Playlist (whole grid) + Playlist (per cell) | |
| Initial state | video_defaults/initial_state | Playing | Global + Playlist (whole grid) + Playlist (per cell) | Cell: `playback_state`. Saved only if Save videos playback status is on. |
| Playback speed | video_defaults/rate | 1.0 | Global + Playlist (whole grid) + Playlist (per cell) | |
| Stream quality | video_defaults/stream_quality | Best | Global + Playlist (whole grid) + Playlist (per cell) | |
| Adapt after | video_defaults/quality_adapt_delay | 15 (s) | Global + Playlist (whole grid) + Playlist (per cell) | |
| On network error | video_defaults/network_retry_mode | Reload a few times | Global + Playlist (whole grid) + Playlist (per cell) | |
| Attempts | video_defaults/network_retry_times | 3 | Global + Playlist (whole grid) + Playlist (per cell) | |
| Auto reload time | video_defaults/auto_reload_timer | 0 (off) | Global + Playlist (whole grid) + Playlist (per cell) | Minutes. |

### Streaming > Link Resolution

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Use Streamlink for HLS streams when possible | streaming/hls_via_streamlink | On | Global | |
| Priority URL resolver | streaming/resolver_priority | yt-dlp | Global | |
| JavaScript runtime | streaming/js_runtime_path | empty | Global | Empty means deno on PATH. Deno is not bundled. |
| Allow JavaScript engines found on PATH | streaming/js_runtime_allow_path | Off | Global | |
| External yt-dlp | streaming/ytdlp_external_path | empty | Global | A path to a yt-dlp program, or `yt-dlp` for the one on PATH. Empty or not found means the built-in yt-dlp module. |
| Resolver priority patterns (list) | streaming/resolver_priority_patterns | empty list | Global | |

### Streaming > SponsorBlock

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Use SponsorBlock on YouTube videos | sponsorblock/enabled | Off | Global | |
| Sponsor | sponsorblock/sponsor | Skip | Global | |
| Unpaid/Self Promotion | sponsorblock/selfpromo | Show in seek bar | Global | |
| Interaction Reminder | sponsorblock/interaction | Show in seek bar | Global | |
| Intermission/Intro Animation | sponsorblock/intro | Disabled | Global | |
| Endcards/Credits | sponsorblock/outro | Disabled | Global | |
| Preview/Recap | sponsorblock/preview | Disabled | Global | |
| Hook/Greetings | sponsorblock/hook | Disabled | Global | |
| Filler Tangent | sponsorblock/filler | Disabled | Global | |
| Non-Music Section | sponsorblock/music_offtopic | Disabled | Global | |
| Highlight | sponsorblock/poi_highlight | Show in seek bar | Global | |

### Streaming > Cookies

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Browser | cookies/from_browser | Off | Global | Only the browser name is saved. The cookies are not. |
| Profile | cookies/browser_profile | empty | Global | |

### Streaming > Network

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Proxy | network/proxy_mode | System | Global | |
| Proxy address | network/proxy_url | empty | Global | |
| Request timeout | network/timeout | 0 | Global | 0 means each library uses its own default. |
| User agent | network/user_agent | empty | Global | Empty means the built-in one. |
| Force IPv4 | network/force_ipv4 | Off | Global | |
| Verify TLS certificates | network/verify_tls | On | Global | |
| Allow http links in https playlists | network/allow_http_in_playlists | On | Global | |

### Plugins > SubtitleCat.com

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Enable SubtitleCat.com | plugins/subtitlecat | Off | Global | |
| Request translations | plugins/subtitlecat_translate | Off | Global | |

### Advanced > Video Decoder

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Decoder | player/video_driver | Hardware (vlc_hw) | Global | On macOS the default is vlc_hw_sp. |
| Videos per process | player/video_driver_players | 4 | Global | |
| VLC Options | misc/vlc_options | empty | Global | |
| Opaque overlay (fix black screen) | internal/opaque_hw_overlay | Off | Global | Experimental. |
| Fake overlay invisibility | internal/fake_overlay_invisibility | Off | Global | Experimental. |
| Force native drag-n-drop for in-window drag | internal/force_native_drag_events | Off | Global | Experimental. |
| HW video border fix | internal/hw_crop_border_offset | Auto | Global | Experimental. |

### Advanced > Logging

| Label | Key | Default | Where | Note |
|---|---|---|---|---|
| Limit log file size | logging/log_limit | Off | Global | |
| Log file size | logging/log_limit_size | 10 (MB) | Global | |
| Log files to keep | logging/log_limit_backups | 1 | Global | |
| Log level | logging/log_level | Warning | Global | |
| Log level (VLC) | logging/log_level_vlc | None | Global | |
