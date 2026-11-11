# Keyboard and mouse shortcuts

This page lists every default shortcut in GridPlayer Alabaster, every mouse
action and drag, and every command that has no key by default. The tables in
the second half are generated from `gridplayer/params/actions.py` and
`gridplayer/params/menu.py` on the `0.2beta-fixes` branch.

## Rules

- **Keys act on the cell under the mouse pointer.** Point at a cell first.
  `Tab` and `Shift+Tab` move the active cell without the mouse.
- **Shift usually means "all cells".** Most one-cell keys have a Shift
  version for every cell (`[` and `Shift+[`, `C` and `Shift+C`, and so on).
- A key works only when its command applies. For example, `S` (next frame)
  does nothing on a live stream, and `E` (Keep) does nothing outside single
  mode.
- Change any shortcut in the **Shortcuts editor**: right-click, **Shortcuts**,
  or Settings (`F6`), **Shortcuts**. See
  [the user guide](../USER-GUIDE.md#21-shortcuts-editor).

## Quick reference

| Task | One cell | All cells |
| --- | --- | --- |
| Play / pause | Click, `Ctrl+Space` | `Space`, Play/Pause media key |
| Next / previous file | `N` / `B` (`PgDown` / `PgUp`) | menu |
| Random file / back | `Shift+N` / `Shift+B` | menu |
| Jump to 0-90% | `0`-`9` | `Alt+0`-`Alt+9` |
| Jump to time | `T` | `Shift+T` |
| Random position | `R` | `Shift+R` |
| Seek 1% | `Left` / `Right` | `Shift+Left` / `Shift+Right` |
| Seek 10% | `;` / `'` | `Shift+;` / `Shift+'` |
| Seek short (5 s) | `Ctrl+Left` / `Ctrl+Right` | `Ctrl+Shift+Left` / `Ctrl+Shift+Right` |
| Seek medium (15 s) | `Ctrl+[` / `Ctrl+]` | `Ctrl+Shift+[` / `Ctrl+Shift+]` |
| Seek long (30 s) | `Ctrl+;` / `Ctrl+'` | `Ctrl+Shift+;` / `Ctrl+Shift+'` |
| Frame back / forward | `D` / `S` | `Shift+D` / `Shift+S` |
| Loop start / end / reset | `[` / `]` / `\` | `Shift+[` / `Shift+]` / `Shift+\` |
| Toggle Loop This File | `Shift+L` | — |
| Speed faster / slower / normal | `C` / `X` / `Z` | `Shift+C` / `Shift+X` / `Shift+Z` |
| Volume up / down | Wheel up / down | menu |
| Mute / unmute | menu (no key) | `M` |
| Audio delay later / earlier | `K` / `J` | `Shift+K` / `Shift+J` |
| Subtitle delay later / earlier | `H` / `G` | `Shift+H` / `Shift+G` |
| Zoom in / out / reset | `.` `+` / `,` `-` / `/` `*`, `Ctrl+Wheel` | add `Shift` |
| Crop left +/- | `U` / `I` | `Shift+U` / `Shift+I` |
| Crop top +/- | `O` / `P` | `Shift+O` / `Shift+P` |
| Crop right +/- | `Alt+U` / `Alt+I` | `Shift+Alt+U` / `Shift+Alt+I` |
| Crop bottom +/- | `Alt+O` / `Alt+P` | `Shift+Alt+O` / `Shift+Alt+P` |
| Crop off | `Y` | `Shift+Y` |
| Move picture | `Alt+Arrows` | `Shift+Alt+Arrows` |
| Screenshot | `Alt+S` | `Shift+Alt+S` |
| Keep (copy to `_keep` folder, then next) | `E` (single mode only) | — |
| Copy file to clipboard | `Ctrl+C` | — |
| Rename title (in app only) | `F4` | — |
| Reload | `F5` | `Shift+F5` |
| Close cell | `Ctrl+F4` | — |
| Open the cell's List window | `L` | — |
| Randomize the cell's list | `Ctrl+Shift+N` | — |
| Single mode | Double-click | — |
| Next / previous cell in single mode | `Media Next` / `Media Previous` | — |
| Shuffle grid | — | `Alt+R` |
| Save snapshot 0-9 | — | `Ctrl+Alt+0`-`Ctrl+Alt+9` |
| Load snapshot 0-9 | — | `Ctrl+0`-`Ctrl+9` |
| Add files / URLs / clipboard | — | `Ctrl+A` / `Ctrl+U` / `Ctrl+V` |
| Open / save / save as / close playlist | — | `Ctrl+O` / `Ctrl+S` / `Ctrl+Shift+S` / `Ctrl+Shift+Q` |
| Fullscreen | — | `F` |
| Leave fullscreen or minimize | — | `Esc` |
| Settings / About / Quit | — | `F6` / `F1` / `Q` |

## Keys that changed from upstream GridPlayer, and reserved keys

| Key | In Alabaster |
| --- | --- |
| `[` / `]` | Set loop start / end (upstream: seek). |
| `Shift+L` | Toggle Loop This File (new). |
| `E` | **Keep**: in single mode, copy the local file to `<folder>_keep` beside its folder, then play the next file. Never moves. Skips a file that is already there. |
| `K` | Audio Delay Later (unchanged). `K` is **not** Keep. |
| `F4` | In-app title Rename (upstream). Does not rename the file on disk. Marked for removal unless a use is found. |
| `F2` | Unbound. Reserved for a future rename on disk. |
| `V`, `Shift+V`, `Shift+M` | Unbound by default. Free to assign. |
| `M` | Mute / unmute all cells. |

### Suggested transform keys (not defaults)

The transform commands and Rotate to fit have no default keys. To set up the
layout the maintainer uses, open the Shortcuts editor and assign:

| Key | Command in the editor |
| --- | --- |
| `V` | Single video > Video > Transform > **Rotate 90** |
| `M` | Single video > Video > Transform > **Rotate 270** (the editor asks to take `M` from Mute / Unmute all cells) |
| `Shift+V` | Single video > Video > Transform > **No Transform** |
| `Shift+M` | Single video > Video > Transform > **Rotate Videos to Fit Cells** (app-wide on/off) |

## Mouse

| Mouse action | Default command |
| --- | --- |
| Click | Play / pause the cell |
| Double-click | Enter or leave single mode |
| Right-click | Opens the cell, grid and program menu |
| Wheel up / down | Volume up / down (one step, 3% by default) |
| `Ctrl` + wheel | Zoom in / out |
| Drag (left button) | Move the video to another cell (fixed) |
| `Shift` held while dropping | Do the other drop action (Add/Replace, Move/Replace) |
| Middle-drag | Move the picture inside its cell |
| `Ctrl` + drag | Zoom into the dragged area (Zoom to Selection) |
| Back / Forward side buttons | No default. Assign them as `Back-Click` / `Forward-Click`. They keep working when **Disable mouse click events** is on. |

A touchpad or smooth-scrolling wheel is counted in whole notches, so one swipe
does not fire a shortcut many times.

**Disable mouse click events** and **Disable mouse wheel events** (Grid >
Playlist Settings) stop clicks and the wheel on cells; keys still work.

## All default keys

The command names below are the ones shown in the menus. "Editor id" is the
internal name, useful when searching the Shortcuts editor or reading
`settings.ini`.

### Default keys: cell

| Command | Keys | Menu path | Editor id |
| --- | --- | --- | --- |
| Play / Pause | `Ctrl+Space`, `Click` | Cell menu | `Play / Pause` |
| Enter Single Mode / Leave Single Mode | `Double Click` | Cell menu | `Single Mode ON / OFF` |
| Previous Video | `Media Previous` | Cell menu | `Previous Video` |
| Next Video | `Media Next` | Cell menu | `Next Video` |
| Play Previous File | `PgUp`, `B` | Cell menu > Playback | `Play Previous File` |
| Play Next File | `PgDown`, `N` | Cell menu > Playback | `Play Next File` |
| Play Random File | `Shift+N`, `Shift+PgDown` | Cell menu > Playback | `Play Random File` |
| Back to Previous Random File | `Shift+B`, `Shift+PgUp` | Cell menu > Playback | `Back From Random File` |
| 0% | `0` | Cell menu > Playback > Jump (to) > Percent | `0%` |
| 10% | `1` | Cell menu > Playback > Jump (to) > Percent | `10%` |
| 20% | `2` | Cell menu > Playback > Jump (to) > Percent | `20%` |
| 30% | `3` | Cell menu > Playback > Jump (to) > Percent | `30%` |
| 40% | `4` | Cell menu > Playback > Jump (to) > Percent | `40%` |
| 50% | `5` | Cell menu > Playback > Jump (to) > Percent | `50%` |
| 60% | `6` | Cell menu > Playback > Jump (to) > Percent | `60%` |
| 70% | `7` | Cell menu > Playback > Jump (to) > Percent | `70%` |
| 80% | `8` | Cell menu > Playback > Jump (to) > Percent | `80%` |
| 90% | `9` | Cell menu > Playback > Jump (to) > Percent | `90%` |
| Timecode | `T` | Cell menu > Playback > Jump (to) | `Timecode` |
| Random | `R` | Cell menu > Playback > Jump (to) | `Random` |
| Next frame | `S` | Cell menu > Playback > Jump (to) | `Next frame` |
| Previous frame | `D` | Cell menu > Playback > Jump (to) | `Previous frame` |
| +1% | `Right` | Cell menu > Playback > Jump (to) | `+1%` |
| +10% | `'` | Cell menu > Playback > Jump (to) | `+10%` |
| -1% | `Left` | Cell menu > Playback > Jump (to) | `-1%` |
| -10% | `;` | Cell menu > Playback > Jump (to) | `-10%` |
| Seek Forward (Short) | `Ctrl+Right` | Cell menu > Playback > Jump (to) | `+5s` |
| Seek Forward (Medium) | `Ctrl+]` | Cell menu > Playback > Jump (to) | `+15s` |
| Seek Forward (Long) | `Ctrl+'` | Cell menu > Playback > Jump (to) | `+30s` |
| Seek Back (Short) | `Ctrl+Left` | Cell menu > Playback > Jump (to) | `-5s` |
| Seek Back (Medium) | `Ctrl+[` | Cell menu > Playback > Jump (to) | `-15s` |
| Seek Back (Long) | `Ctrl+;` | Cell menu > Playback > Jump (to) | `-30s` |
| Set Loop Start | `[` | Cell menu > Playback > Loop | `Set Loop Start` |
| Set Loop End | `]` | Cell menu > Playback > Loop | `Set Loop End` |
| Loop Reset | `\` | Cell menu > Playback > Loop | `Loop Reset` |
| Toggle Loop File | `Shift+L` | Cell menu > Playback > Loop | `Toggle Loop File` |
| List… | `L` | Cell menu > Playback | `List` |
| Randomize List | `Ctrl+Shift+N` | Cell menu > Playback | `Randomize List` |
| Faster | `C` | Cell menu > Playback > Speed | `Faster` |
| Slower | `X` | Cell menu > Playback > Speed | `Slower` |
| Normal | `Z` | Cell menu > Playback > Speed | `Normal` |
| Zoom In | `.`, `+`, `Ctrl+Wheel-Up` | Cell menu > Video > Zoom | `Zoom In` |
| Zoom Out | `,`, `-`, `Ctrl+Wheel-Down` | Cell menu > Video > Zoom | `Zoom Out` |
| Zoom Reset | `/`, `*` | Cell menu > Video > Zoom | `Zoom Reset` |
| Crop Left + | `U` | Cell menu > Video > Crop | `Crop Left +` |
| Crop Left - | `I` | Cell menu > Video > Crop | `Crop Left -` |
| Crop Top + | `O` | Cell menu > Video > Crop | `Crop Top +` |
| Crop Top - | `P` | Cell menu > Video > Crop | `Crop Top -` |
| Crop Right + | `Alt+U` | Cell menu > Video > Crop | `Crop Right +` |
| Crop Right - | `Alt+I` | Cell menu > Video > Crop | `Crop Right -` |
| Crop Bottom + | `Alt+O` | Cell menu > Video > Crop | `Crop Bottom +` |
| Crop Bottom - | `Alt+P` | Cell menu > Video > Crop | `Crop Bottom -` |
| Crop Reset | `Y` | Cell menu > Video > Crop | `Crop Reset` |
| Move Left | `Alt+Left` | Cell menu > Video > Position | `Move Left` |
| Move Right | `Alt+Right` | Cell menu > Video > Position | `Move Right` |
| Move Up | `Alt+Up` | Cell menu > Video > Position | `Move Up` |
| Move Down | `Alt+Down` | Cell menu > Video > Position | `Move Down` |
| Take Screenshot | `Alt+S` | Cell menu > Video | `Take Screenshot` |
| Later | `K` | Cell menu > Audio > Audio Delay | `Audio Delay Later` |
| Earlier | `J` | Cell menu > Audio > Audio Delay | `Audio Delay Earlier` |
| Later | `H` | Cell menu > Subtitles > Subtitle Delay | `Subtitle Delay Later` |
| Earlier | `G` | Cell menu > Subtitles > Subtitle Delay | `Subtitle Delay Earlier` |
| Increase Volume | `Wheel-Up` | Cell menu > Audio | `Audio Volume - Increase` |
| Decrease Volume | `Wheel-Down` | Cell menu > Audio | `Audio Volume - Decrease` |
| Keep | `E` | Cell menu > File | `Keep File` |
| Copy File | `Ctrl+C` | Cell menu > File | `Copy File` |
| Rename | `F4` | Cell menu | `Rename` |
| Reload | `F5` | Cell menu | `Reload` |
| Close | `Ctrl+F4` | Cell menu | `Close` |

### Default keys: all cells

| Command | Keys | Menu path | Editor id |
| --- | --- | --- | --- |
| Play / Pause (all cells) | `Space`, `Media Play`, `Toggle Media Play/Pause` | [ALL] | `Play / Pause [ALL]` |
| Pause (all cells) | `Media Pause` | [ALL] | `Pause [ALL]` |
| Stop (all cells) | `Media Stop` | [ALL] | `Stop [ALL]` |
| 0% (all cells) | `Alt+0` | [ALL] > Playback > Jump (to) > Percent | `0% [ALL]` |
| 10% (all cells) | `Alt+1` | [ALL] > Playback > Jump (to) > Percent | `10% [ALL]` |
| 20% (all cells) | `Alt+2` | [ALL] > Playback > Jump (to) > Percent | `20% [ALL]` |
| 30% (all cells) | `Alt+3` | [ALL] > Playback > Jump (to) > Percent | `30% [ALL]` |
| 40% (all cells) | `Alt+4` | [ALL] > Playback > Jump (to) > Percent | `40% [ALL]` |
| 50% (all cells) | `Alt+5` | [ALL] > Playback > Jump (to) > Percent | `50% [ALL]` |
| 60% (all cells) | `Alt+6` | [ALL] > Playback > Jump (to) > Percent | `60% [ALL]` |
| 70% (all cells) | `Alt+7` | [ALL] > Playback > Jump (to) > Percent | `70% [ALL]` |
| 80% (all cells) | `Alt+8` | [ALL] > Playback > Jump (to) > Percent | `80% [ALL]` |
| 90% (all cells) | `Alt+9` | [ALL] > Playback > Jump (to) > Percent | `90% [ALL]` |
| Timecode (all cells) | `Shift+T` | [ALL] > Playback > Jump (to) | `Timecode [ALL]` |
| Random (all cells) | `Shift+R` | [ALL] > Playback > Jump (to) | `Random [ALL]` |
| Next frame (all cells) | `Shift+S` | [ALL] > Playback > Jump (to) | `Next frame [ALL]` |
| Previous frame (all cells) | `Shift+D` | [ALL] > Playback > Jump (to) | `Previous frame [ALL]` |
| +1% (all cells) | `Shift+Right` | [ALL] > Playback > Jump (to) | `+1% [ALL]` |
| +10% (all cells) | `Shift+'` | [ALL] > Playback > Jump (to) | `+10% [ALL]` |
| -1% (all cells) | `Shift+Left` | [ALL] > Playback > Jump (to) | `-1% [ALL]` |
| -10% (all cells) | `Shift+;` | [ALL] > Playback > Jump (to) | `-10% [ALL]` |
| Seek Forward (Short) (all cells) | `Ctrl+Shift+Right` | [ALL] > Playback > Jump (to) | `+5s [ALL]` |
| Seek Forward (Medium) (all cells) | `Ctrl+Shift+]` | [ALL] > Playback > Jump (to) | `+15s [ALL]` |
| Seek Forward (Long) (all cells) | `Ctrl+Shift+'` | [ALL] > Playback > Jump (to) | `+30s [ALL]` |
| Seek Back (Short) (all cells) | `Ctrl+Shift+Left` | [ALL] > Playback > Jump (to) | `-5s [ALL]` |
| Seek Back (Medium) (all cells) | `Ctrl+Shift+[` | [ALL] > Playback > Jump (to) | `-15s [ALL]` |
| Seek Back (Long) (all cells) | `Ctrl+Shift+;` | [ALL] > Playback > Jump (to) | `-30s [ALL]` |
| Set Loop Start (all cells) | `Shift+[` | [ALL] > Playback > Loop | `Set Loop Start [ALL]` |
| Set Loop End (all cells) | `Shift+]` | [ALL] > Playback > Loop | `Set Loop End [ALL]` |
| Loop Reset (all cells) | `Shift+\` | [ALL] > Playback > Loop | `Loop Reset [ALL]` |
| Faster (all cells) | `Shift+C` | [ALL] > Playback > Speed | `Faster [ALL]` |
| Slower (all cells) | `Shift+X` | [ALL] > Playback > Speed | `Slower [ALL]` |
| Normal (all cells) | `Shift+Z` | [ALL] > Playback > Speed | `Normal [ALL]` |
| Zoom In (all cells) | `Shift+.`, `Shift++` | [ALL] > Video > Zoom | `Zoom In [ALL]` |
| Zoom Out (all cells) | `Shift+,`, `Shift+-` | [ALL] > Video > Zoom | `Zoom Out [ALL]` |
| Zoom Reset (all cells) | `Shift+/`, `Shift+*` | [ALL] > Video > Zoom | `Zoom Reset [ALL]` |
| Crop Left + (all cells) | `Shift+U` | [ALL] > Video > Crop | `Crop Left + [ALL]` |
| Crop Left - (all cells) | `Shift+I` | [ALL] > Video > Crop | `Crop Left - [ALL]` |
| Crop Top + (all cells) | `Shift+O` | [ALL] > Video > Crop | `Crop Top + [ALL]` |
| Crop Top - (all cells) | `Shift+P` | [ALL] > Video > Crop | `Crop Top - [ALL]` |
| Crop Right + (all cells) | `Shift+Alt+U` | [ALL] > Video > Crop | `Crop Right + [ALL]` |
| Crop Right - (all cells) | `Shift+Alt+I` | [ALL] > Video > Crop | `Crop Right - [ALL]` |
| Crop Bottom + (all cells) | `Shift+Alt+O` | [ALL] > Video > Crop | `Crop Bottom + [ALL]` |
| Crop Bottom - (all cells) | `Shift+Alt+P` | [ALL] > Video > Crop | `Crop Bottom - [ALL]` |
| Crop Reset (all cells) | `Shift+Y` | [ALL] > Video > Crop | `Crop Reset [ALL]` |
| Move Left (all cells) | `Shift+Alt+Left` | [ALL] > Video > Position | `Move Left [ALL]` |
| Move Right (all cells) | `Shift+Alt+Right` | [ALL] > Video > Position | `Move Right [ALL]` |
| Move Up (all cells) | `Shift+Alt+Up` | [ALL] > Video > Position | `Move Up [ALL]` |
| Move Down (all cells) | `Shift+Alt+Down` | [ALL] > Video > Position | `Move Down [ALL]` |
| Take Screenshot (all cells) | `Shift+Alt+S` | [ALL] > Video | `Take Screenshot [ALL]` |
| Later (all cells) | `Shift+K` | [ALL] > Audio > Audio Delay | `Audio Delay Later [ALL]` |
| Earlier (all cells) | `Shift+J` | [ALL] > Audio > Audio Delay | `Audio Delay Earlier [ALL]` |
| Mute / Unmute (all cells) | `M` | keymap only (no menu item) | `Audio Volume - Mute / Unmute [ALL]` |
| Later (all cells) | `Shift+H` | [ALL] > Subtitles > Subtitle Delay | `Subtitle Delay Later [ALL]` |
| Earlier (all cells) | `Shift+G` | [ALL] > Subtitles > Subtitle Delay | `Subtitle Delay Earlier [ALL]` |
| Reload (all cells) | `Shift+F5` | [ALL] | `Reload [ALL]` |

### Default keys: grid and program

| Command | Keys | Menu path | Editor id |
| --- | --- | --- | --- |
| Shuffle | `Alt+R` | Grid menu > Grid | `Shuffle Grid` |
| Save Snapshot (0) | `Ctrl+Alt+0` | Snapshots > Save Snapshot | `Save Snapshot (0)` |
| Save Snapshot (1) | `Ctrl+Alt+1` | Snapshots > Save Snapshot | `Save Snapshot (1)` |
| Save Snapshot (2) | `Ctrl+Alt+2` | Snapshots > Save Snapshot | `Save Snapshot (2)` |
| Save Snapshot (3) | `Ctrl+Alt+3` | Snapshots > Save Snapshot | `Save Snapshot (3)` |
| Save Snapshot (4) | `Ctrl+Alt+4` | Snapshots > Save Snapshot | `Save Snapshot (4)` |
| Save Snapshot (5) | `Ctrl+Alt+5` | Snapshots > Save Snapshot | `Save Snapshot (5)` |
| Save Snapshot (6) | `Ctrl+Alt+6` | Snapshots > Save Snapshot | `Save Snapshot (6)` |
| Save Snapshot (7) | `Ctrl+Alt+7` | Snapshots > Save Snapshot | `Save Snapshot (7)` |
| Save Snapshot (8) | `Ctrl+Alt+8` | Snapshots > Save Snapshot | `Save Snapshot (8)` |
| Save Snapshot (9) | `Ctrl+Alt+9` | Snapshots > Save Snapshot | `Save Snapshot (9)` |
| Load Snapshot (0) | `Ctrl+0` | Snapshots | `Load Snapshot (0)` |
| Load Snapshot (1) | `Ctrl+1` | Snapshots | `Load Snapshot (1)` |
| Load Snapshot (2) | `Ctrl+2` | Snapshots | `Load Snapshot (2)` |
| Load Snapshot (3) | `Ctrl+3` | Snapshots | `Load Snapshot (3)` |
| Load Snapshot (4) | `Ctrl+4` | Snapshots | `Load Snapshot (4)` |
| Load Snapshot (5) | `Ctrl+5` | Snapshots | `Load Snapshot (5)` |
| Load Snapshot (6) | `Ctrl+6` | Snapshots | `Load Snapshot (6)` |
| Load Snapshot (7) | `Ctrl+7` | Snapshots | `Load Snapshot (7)` |
| Load Snapshot (8) | `Ctrl+8` | Snapshots | `Load Snapshot (8)` |
| Load Snapshot (9) | `Ctrl+9` | Snapshots | `Load Snapshot (9)` |
| Fullscreen | `F` | Program menu | `Fullscreen` |
| Leave Fullscreen or Minimize | `Esc` | keymap only (no menu item) | `Leave Fullscreen or Minimize` |
| Add Files | `Ctrl+A` | Program menu > Add | `Add - Files` |
| Add URL(s) | `Ctrl+U` | Program menu > Add | `Add - URL(s)` |
| From Clipboard | `Ctrl+V` | Program menu > Add | `Add - Clipboard` |
| Open Playlist | `Ctrl+O` | Program menu | `Open Playlist` |
| Save Playlist | `Ctrl+S` | Program menu | `Save Playlist` |
| Save Playlist As | `Ctrl+Shift+S` | Program menu | `Save Playlist As` |
| Close Playlist | `Ctrl+Shift+Q` | Program menu | `Close Playlist` |
| Settings | `F6` | Program menu | `Settings` |
| About | `F1` | Program menu | `About` |
| Quit | `Q` | Program menu | `Quit` |
| Next Active | `Tab` | keymap only (no menu item) | `Next Active` |
| Previous Active | `Shift+Tab` | keymap only (no menu item) | `Previous Active` |

## Commands with no default key

These commands are on the menus but have no key until you give them one in the Shortcuts editor. Preset lists (aspect ratios, crop shapes, slide durations, deinterlace modes, snapshot delete slots) are summarized by their menu.

### Cell

| Command | Menu path | Editor id |
| --- | --- | --- |
| Stop | Cell menu | `Stop` |
| Include Subfolders | Cell menu > Playback | `Include Subfolders` |
| All Media | Cell menu > Playback > Files to Play | `Media Kind ALL` |
| Videos Only | Cell menu > Playback > Files to Play | `Media Kind VIDEOS_ONLY` |
| Images Only | Cell menu > Playback > Files to Play | `Media Kind IMAGES_ONLY` |
| (each choice) | Cell menu > Playback > Slide Duration | — |
| +5% | Cell menu > Playback > Jump (to) | `+5%` |
| -5% | Cell menu > Playback > Jump (to) | `-5%` |
| Previous Chapter | Cell menu > Playback > Chapters | `Previous Chapter` |
| Next Chapter | Cell menu > Playback > Chapters | `Next Chapter` |
| Chapters | Cell menu > Playback > Chapters | `Chapter List` |
| Add Bookmark | Cell menu > Playback > Bookmarks | `Add Bookmark` |
| Previous Bookmark | Cell menu > Playback > Bookmarks | `Previous Bookmark` |
| Next Bookmark | Cell menu > Playback > Bookmarks | `Next Bookmark` |
| Bookmarks | Cell menu > Playback > Bookmarks | `Bookmark List` |
| Manage Bookmarks… | Cell menu > Playback > Bookmarks | `Manage Bookmarks` |
| Random Loop | Cell menu > Playback > Loop | `Random Loop` |
| Loop Chapter | Cell menu > Playback > Loop | `Loop Chapter` |
| Off | Cell menu > Playback > Other Orientation | `Aspect Filter OFF` |
| Skip Other Orientation | Cell menu > Playback > Other Orientation | `Aspect Filter REJECT` |
| Ask on Other Orientation | Cell menu > Playback > Other Orientation | `Aspect Filter ASK` |
| Loop This File | Cell menu > Playback > When Finished | `When Finished Loop File` |
| Play Next File | Cell menu > Playback > When Finished | `When Finished Next` |
| Play Previous File | Cell menu > Playback > When Finished | `When Finished Previous` |
| Play Random File | Cell menu > Playback > When Finished | `When Finished Shuffle` |
| Leave the List | Cell menu > Playback | `Leave the List` |
| Start Over | Cell menu > Playback > At the End of the List | `List End Start Over` |
| Pause At Start | Cell menu > Playback > At the End of the List | `List End Pause` |
| Stop | Cell menu > Playback > At the End of the List | `List End Stop` |
| Close | Cell menu > Playback > At the End of the List | `List End Close` |
| Show Error | Cell menu > Playback > When Video Fails | `When Video Fails Show Error` |
| Play Next | Cell menu > Playback > When Video Fails | `When Video Fails Play Next` |
| Set Next After | Cell menu > Playback > When Video Fails | `When Video Fails Next After: %v` |
| Pause At Start | Cell menu > Playback > When Finished | `When Finished Pause` |
| Stop | Cell menu > Playback > When Finished | `When Finished Stop` |
| Close | Cell menu > Playback > When Finished | `When Finished Close` |
| Zoom to Selection | Cell menu > Video > Zoom | `Zoom to Selection` |
| Zoom to Cursor | Cell menu > Video > Zoom | `Zoom to Cursor` |
| Set Crop | Cell menu > Video > Crop | `Set Crop` |
| The list's | Cell menu > Video > Crop | `Crop List` |
| (each choice) | Cell menu > Video > Crop | — |
| Move Past Edges | Cell menu > Video > Position | `Move Past Edges` |
| Set Position | Cell menu > Video > Position | `Set Position` |
| Position Reset | Cell menu > Video > Position | `Position Reset` |
| Align Center | Cell menu > Video > Position | `Align Center` |
| Align Top | Cell menu > Video > Position | `Align Top` |
| Align Bottom | Cell menu > Video > Position | `Align Bottom` |
| Align Left | Cell menu > Video > Position | `Align Left` |
| Align Right | Cell menu > Video > Position | `Align Right` |
| Align Top Left | Cell menu > Video > Position | `Align Top Left` |
| Align Top Right | Cell menu > Video > Position | `Align Top Right` |
| Align Bottom Left | Cell menu > Video > Position | `Align Bottom Left` |
| Align Bottom Right | Cell menu > Video > Position | `Align Bottom Right` |
| Fill | Cell menu > Video > View Mode | `View Mode Fill` |
| Fit | Cell menu > Video > View Mode | `View Mode Fit` |
| Stretch | Cell menu > Video > View Mode | `View Mode Stretch` |
| The list's | Cell menu > Video > Aspect Ratio | `Aspect Ratio List` |
| Default | Cell menu > Video > Aspect Ratio | `Aspect Ratio Default` |
| (each choice) | Cell menu > Video > Aspect Ratio | — |
| Rotate 90 | Cell menu > Video > Transform | `Rotate 90` |
| Rotate 180 | Cell menu > Video > Transform | `Rotate 180` |
| Rotate 270 | Cell menu > Video > Transform | `Rotate 270` |
| Flip Horizontally | Cell menu > Video > Transform | `Flip Horizontally` |
| Flip Vertically | Cell menu > Video > Transform | `Flip Vertically` |
| Transpose | Cell menu > Video > Transform | `Transpose` |
| Anti-transpose | Cell menu > Video > Transform | `Anti-transpose` |
| No Transform | Cell menu > Video > Transform | `No Transform` |
| Rotate Videos to Fit Cells | Cell menu > Video > Transform | `Rotate to Fit` |
| Automatic | Cell menu > Video > Deinterlace | `Deinterlace Auto` |
| On | Cell menu > Video > Deinterlace | `Deinterlace On` |
| Off | Cell menu > Video > Deinterlace | `Deinterlace Off` |
| (each choice) | Cell menu > Video > Deinterlace | — |
| Sync By Percent | Cell menu > Sync Others | `Seek Others (Percent)` |
| Sync By Timecode | Cell menu > Sync Others | `Seek Others (Timecode)` |
| Zoom and Position | Cell menu > Sync Others | `Sync Others (Zoom and Position)` |
| Stream Quality | Cell menu | `Stream Quality` |
| Video Track | Cell menu > Video | `Video Track` |
| Audio Track | Cell menu > Audio | `Audio Track` |
| Audio Device | Cell menu > Audio | `Audio Device` |
| Set Delay | Cell menu > Audio > Audio Delay | `Audio Delay: %v` |
| Reset | Cell menu > Audio > Audio Delay | `Audio Delay Reset` |
| Subtitle Track | Cell menu > Subtitles | `Subtitle Track` |
| Set Delay | Cell menu > Subtitles > Subtitle Delay | `Subtitle Delay: %v` |
| Reset | Cell menu > Subtitles > Subtitle Delay | `Subtitle Delay Reset` |
| Find subtitles on SubtitleCat.com… | Cell menu > Subtitles | `Find Subtitles on SubtitleCat` |
| (each choice) | Cell menu > Audio > Audio Mode | — |
| Mute / Unmute | Cell menu > Audio | `Audio Volume - Mute / Unmute` |
| Copy File Name | Cell menu > File | `Copy File Name` |
| Copy File Path | Cell menu > File | `Copy File Path` |
| Show in Folder | Cell menu > File | `Show in Folder` |
| Copy URL | Cell menu > URL | `Copy URL` |
| Copy URL at Current Time | Cell menu > URL | `Copy URL at Current Time` |
| Open in Browser | Cell menu > URL | `Open in Browser` |
| Set Auto Reload | Cell menu | `Auto Reload: %v` |
| Show Error | Cell menu > On Network Error | `On Network Error Show Error` |
| Reload a Few Times | Cell menu > On Network Error | `On Network Error Retry Times` |
| Keep Reloading | Cell menu > On Network Error | `On Network Error Retry Forever` |
| Set Attempts | Cell menu > On Network Error | `On Network Error Attempts: %v` |

### All cells

| Command | Menu path | Editor id |
| --- | --- | --- |
| Play (all cells) | [ALL] | `Play [ALL]` |
| Play Previous File (all cells) | [ALL] > Playback | `Play Previous File [ALL]` |
| Play Next File (all cells) | [ALL] > Playback | `Play Next File [ALL]` |
| Play Random File (all cells) | [ALL] > Playback | `Play Random File [ALL]` |
| On (all cells) | [ALL] > Playback > Include Subfolders | `Include Subfolders On [ALL]` |
| Off (all cells) | [ALL] > Playback > Include Subfolders | `Include Subfolders Off [ALL]` |
| Off (all cells) | [ALL] > Playback > Other Orientation | `Aspect Filter OFF [ALL]` |
| Skip Other Orientation (all cells) | [ALL] > Playback > Other Orientation | `Aspect Filter REJECT [ALL]` |
| Ask on Other Orientation (all cells) | [ALL] > Playback > Other Orientation | `Aspect Filter ASK [ALL]` |
| All Media (all cells) | [ALL] > Playback > Files to Play | `Media Kind ALL [ALL]` |
| Videos Only (all cells) | [ALL] > Playback > Files to Play | `Media Kind VIDEOS_ONLY [ALL]` |
| Images Only (all cells) | [ALL] > Playback > Files to Play | `Media Kind IMAGES_ONLY [ALL]` |
| +5% (all cells) | [ALL] > Playback > Jump (to) | `+5% [ALL]` |
| -5% (all cells) | [ALL] > Playback > Jump (to) | `-5% [ALL]` |
| Previous Chapter (all cells) | [ALL] > Playback > Chapters | `Previous Chapter [ALL]` |
| Next Chapter (all cells) | [ALL] > Playback > Chapters | `Next Chapter [ALL]` |
| Previous Bookmark (all cells) | [ALL] > Playback > Bookmarks | `Previous Bookmark [ALL]` |
| Next Bookmark (all cells) | [ALL] > Playback > Bookmarks | `Next Bookmark [ALL]` |
| On (all cells) | [ALL] > Playback > Loop > Random Loop | `Random Loop On [ALL]` |
| Off (all cells) | [ALL] > Playback > Loop > Random Loop | `Random Loop Off [ALL]` |
| Loop Chapter (all cells) | [ALL] > Playback > Loop | `Loop Chapter [ALL]` |
| Loop This File (all cells) | [ALL] > Playback > When Finished | `When Finished Loop File [ALL]` |
| Play Next File (all cells) | [ALL] > Playback > When Finished | `When Finished Next [ALL]` |
| Play Previous File (all cells) | [ALL] > Playback > When Finished | `When Finished Previous [ALL]` |
| Play Random File (all cells) | [ALL] > Playback > When Finished | `When Finished Shuffle [ALL]` |
| Start Over (all cells) | [ALL] > Playback > At the End of the List | `List End Start Over [ALL]` |
| Pause At Start (all cells) | [ALL] > Playback > At the End of the List | `List End Pause [ALL]` |
| Stop (all cells) | [ALL] > Playback > At the End of the List | `List End Stop [ALL]` |
| Close (all cells) | [ALL] > Playback > At the End of the List | `List End Close [ALL]` |
| Show Error (all cells) | [ALL] > Playback > When Video Fails | `When Video Fails Show Error [ALL]` |
| Play Next (all cells) | [ALL] > Playback > When Video Fails | `When Video Fails Play Next [ALL]` |
| Set Next After (all cells) | [ALL] > Playback > When Video Fails | `When Video Fails Next After [ALL]` |
| Pause At Start (all cells) | [ALL] > Playback > When Finished | `When Finished Pause [ALL]` |
| Stop (all cells) | [ALL] > Playback > When Finished | `When Finished Stop [ALL]` |
| Close (all cells) | [ALL] > Playback > When Finished | `When Finished Close [ALL]` |
| On (all cells) | [ALL] > Video > Zoom > Zoom to Cursor | `Zoom to Cursor On [ALL]` |
| Off (all cells) | [ALL] > Video > Zoom > Zoom to Cursor | `Zoom to Cursor Off [ALL]` |
| (each choice) | [ALL] > Video > Crop | — |
| On (all cells) | [ALL] > Video > Position > Move Past Edges | `Move Past Edges On [ALL]` |
| Off (all cells) | [ALL] > Video > Position > Move Past Edges | `Move Past Edges Off [ALL]` |
| Position Reset (all cells) | [ALL] > Video > Position | `Position Reset [ALL]` |
| Align Center (all cells) | [ALL] > Video > Position | `Align Center [ALL]` |
| Align Top (all cells) | [ALL] > Video > Position | `Align Top [ALL]` |
| Align Bottom (all cells) | [ALL] > Video > Position | `Align Bottom [ALL]` |
| Align Left (all cells) | [ALL] > Video > Position | `Align Left [ALL]` |
| Align Right (all cells) | [ALL] > Video > Position | `Align Right [ALL]` |
| Align Top Left (all cells) | [ALL] > Video > Position | `Align Top Left [ALL]` |
| Align Top Right (all cells) | [ALL] > Video > Position | `Align Top Right [ALL]` |
| Align Bottom Left (all cells) | [ALL] > Video > Position | `Align Bottom Left [ALL]` |
| Align Bottom Right (all cells) | [ALL] > Video > Position | `Align Bottom Right [ALL]` |
| Fill (all cells) | [ALL] > Video > View Mode | `View Mode Fill [ALL]` |
| Fit (all cells) | [ALL] > Video > View Mode | `View Mode Fit [ALL]` |
| Stretch (all cells) | [ALL] > Video > View Mode | `View Mode Stretch [ALL]` |
| Default (all cells) | [ALL] > Video > Aspect Ratio | `Aspect Ratio Default [ALL]` |
| (each choice) | [ALL] > Video > Aspect Ratio | — |
| Rotate 90 (all cells) | [ALL] > Video > Transform | `Rotate 90 [ALL]` |
| Rotate 180 (all cells) | [ALL] > Video > Transform | `Rotate 180 [ALL]` |
| Rotate 270 (all cells) | [ALL] > Video > Transform | `Rotate 270 [ALL]` |
| Flip Horizontally (all cells) | [ALL] > Video > Transform | `Flip Horizontally [ALL]` |
| Flip Vertically (all cells) | [ALL] > Video > Transform | `Flip Vertically [ALL]` |
| Transpose (all cells) | [ALL] > Video > Transform | `Transpose [ALL]` |
| Anti-transpose (all cells) | [ALL] > Video > Transform | `Anti-transpose [ALL]` |
| No Transform (all cells) | [ALL] > Video > Transform | `No Transform [ALL]` |
| (each choice) | [ALL] > Audio > Audio Mode | — |
| Set Delay (all cells) | [ALL] > Audio > Audio Delay | `Audio Delay Set [ALL]` |
| Reset (all cells) | [ALL] > Audio > Audio Delay | `Audio Delay Reset [ALL]` |
| Increase Volume (all cells) | [ALL] > Audio | `Audio Volume - Increase [ALL]` |
| Decrease Volume (all cells) | [ALL] > Audio | `Audio Volume - Decrease [ALL]` |
| Mute (all cells) | [ALL] > Audio | `Audio Volume - Mute [ALL]` |
| Unmute (all cells) | [ALL] > Audio | `Audio Volume - Unmute [ALL]` |
| Set Delay (all cells) | [ALL] > Subtitles > Subtitle Delay | `Subtitle Delay Set [ALL]` |
| Reset (all cells) | [ALL] > Subtitles > Subtitle Delay | `Subtitle Delay Reset [ALL]` |
| Auto Reload (all cells) | [ALL] | `Auto Reload [ALL]` |
| Copy Paths and URLs (all cells) | [ALL] | `Copy Paths and URLs [ALL]` |

### Grid and program

| Command | Menu path | Editor id |
| --- | --- | --- |
| Disabled | Grid menu > Sync > Seek | `Seek Sync (Disabled)` |
| Sync By Percent | Grid menu > Sync > Seek | `Seek Sync (Percent)` |
| Sync By Timecode | Grid menu > Sync > Seek | `Seek Sync (Timecode)` |
| Zoom and Position | Grid menu > Sync | `Sync Zoom and Position` |
| Play / Pause | Grid menu > Sync | `Sync Play / Pause` |
| Speed | Grid menu > Sync | `Sync Speed` |
| Shuffle On Load | Grid menu > Grid | `Shuffle Grid On Load` |
| Auto (Rows First) | Grid menu > Grid | `Rows First` |
| Auto (Columns First) | Grid menu > Grid | `Columns First` |
| Fit Cells | Grid menu > Grid | `Fit Cells` |
| Set Size | Grid menu > Grid | `Size: %v` |
| Fixed Grid | Grid menu > Grid | `Fixed Grid` |
| Set Grid Size | Grid menu > Grid | `Grid Size: %v` |
| Show All Cells | Grid menu > Grid | `Show All Cells` |
| (each choice) | Snapshots > Delete Snapshot | — |
| Edit Playlist Settings… | Grid menu > Playlist Settings | `Edit Playlist Settings` |
| Bookmarks in Playlist… | Grid menu > Playlist Settings | `Bookmarks in Playlist` |
| Lists in Playlist… | Grid menu > Playlist Settings | `Lists in Playlist` |
| Share bookmarks between cells with the same file | Grid menu > Playlist Settings | `Share Bookmarks` |
| Disable Mouse Click Events | Grid menu > Playlist Settings | `Disable Mouse Click Events` |
| Disable Mouse Wheel Events | Grid menu > Playlist Settings | `Disable Mouse Wheel Events` |
| Disable Overlay | Grid menu > Playlist Settings | `Disable Overlay` |
| Pause background videos on single mode | Grid menu > Playlist Settings | `Pause Background Videos` |
| Pause videos when minimized | Grid menu > Playlist Settings | `Pause When Minimized` |
| Show overlay border for active video | Grid menu > Playlist Settings | `Show Overlay Border` |
| Hide overlay after timeout | Grid menu > Playlist Settings | `Hide Overlay After Timeout` |
| Minimize | Program menu | `Minimize` |
| Add Folder | Program menu > Add | `Add - Folder` |
| Recent | Program menu > Add | `Add - Recent Videos` |
| Recent Playlists | Program menu | `Open Playlist (Recent)` |
| Shortcuts | Program menu | `Shortcuts` |
