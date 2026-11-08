# Hotkeys by task

The default keys, grouped by what you're doing. Verified against the app's
default keymap. Change any of them on the Shortcuts page (Settings,
Shortcuts, or right-click, **Shortcuts**); **Reset all** brings the
defaults back. The [generated list](hotkeys.md) has every key with its
internal name.

**Keys act on the cell under the mouse pointer.** "Every cell" keys act on
the whole grid.

## Play and move between files

| Do | This cell | Every cell |
| --- | --- | --- |
| Play / pause | `Ctrl+Space`, Click | `Space`, Media Play/Pause |
| Pause | | Media Pause |
| Stop | | Media Stop |
| Next file | `N`, `PgDown` | |
| Previous file | `B`, `PgUp` | |
| Random file | `Shift+N`, `Shift+PgDown` | |
| Back to the previous random file | `Shift+B`, `Shift+PgUp` | |
| Single Mode on / off | Double-click | |
| Next / previous cell in Single Mode | | Media Next / Media Previous |
| Keep (copy to `<folder>_keep`, play next; Single Mode only) | `E` | |
| List window (single-cell list) | `L` | |
| Randomize the cell's list | `Ctrl+Shift+N` | |
| Reload | `F5` | `Shift+F5` |
| Close the cell | `Ctrl+F4` | |

## Seek

| Do | This cell | Every cell |
| --- | --- | --- |
| Jump to 0%, 10% ... 90% | `0` ... `9` | `Alt+0` ... `Alt+9` |
| Jump to a time | `T` | `Shift+T` |
| Jump somewhere random | `R` | `Shift+R` |
| +1% / -1% | `Right` / `Left` | `Shift+Right` / `Shift+Left` |
| +10% / -10% | `'` / `;` | `Shift+'` / `Shift+;` |
| +5 s / -5 s (short step) | `Ctrl+Right` / `Ctrl+Left` | `Ctrl+Shift+Right` / `Ctrl+Shift+Left` |
| +15 s / -15 s (medium step) | `Ctrl+]` / `Ctrl+[` | `Ctrl+Shift+]` / `Ctrl+Shift+[` |
| +30 s / -30 s (long step) | `Ctrl+'` / `Ctrl+;` | `Ctrl+Shift+'` / `Ctrl+Shift+;` |
| Next frame / previous frame | `S` / `D` | `Shift+S` / `Shift+D` |

The second steps follow Settings, Defaults, Playlist, Step Sizes; the menu
shows the lengths you set.

## Loops

| Do | This cell | Every cell |
| --- | --- | --- |
| Set loop start (A) | `[` | `Shift+[` |
| Set loop end (B) | `]` | `Shift+]` |
| Loop reset | `\` | `Shift+\` |
| Toggle Loop This File | `Shift+L` | |

## Speed

| Do | This cell | Every cell |
| --- | --- | --- |
| Faster | `C` | `Shift+C` |
| Slower | `X` | `Shift+X` |
| Normal speed | `Z` | `Shift+Z` |

## Sound

| Do | This cell | Every cell |
| --- | --- | --- |
| Volume up / down | Wheel up / down | |
| Mute / unmute | | `M` |
| Audio later / earlier (50 ms) | `K` / `J` | `Shift+K` / `Shift+J` |
| Subtitles later / earlier (100 ms) | `H` / `G` | `Shift+H` / `Shift+G` |

## Picture

| Do | This cell | Every cell |
| --- | --- | --- |
| Zoom in | `.`, `+`, `Ctrl`+wheel up | `Shift+.`, `Shift++` |
| Zoom out | `,`, `-`, `Ctrl`+wheel down | `Shift+,`, `Shift+-` |
| Zoom reset | `/`, `*` | `Shift+/`, `Shift+*` |
| Crop left more / less | `U` / `I` | `Shift+U` / `Shift+I` |
| Crop top more / less | `O` / `P` | `Shift+O` / `Shift+P` |
| Crop right more / less | `Alt+U` / `Alt+I` | `Shift+Alt+U` / `Shift+Alt+I` |
| Crop bottom more / less | `Alt+O` / `Alt+P` | `Shift+Alt+O` / `Shift+Alt+P` |
| Crop off | `Y` | `Shift+Y` |
| Move picture left / right / up / down | `Alt+Left` / `Alt+Right` / `Alt+Up` / `Alt+Down` | `Shift+Alt+` arrows |
| Screenshot | `Alt+S` | `Shift+Alt+S` |

## Grid and snapshots

| Do | Key |
| --- | --- |
| Shuffle the grid | `Alt+R` |
| Save snapshot to slot 0-9 | `Ctrl+Alt+0` ... `Ctrl+Alt+9` |
| Load snapshot from slot 0-9 | `Ctrl+0` ... `Ctrl+9` |
| Next / previous active cell | `Tab` / `Shift+Tab` |

## Files, playlists and the app

| Do | Key |
| --- | --- |
| Add files | `Ctrl+A` |
| Add URL(s) | `Ctrl+U` |
| Add from clipboard | `Ctrl+V` |
| Copy the cell's file | `Ctrl+C` |
| Open playlist | `Ctrl+O` |
| Save playlist | `Ctrl+S` |
| Save playlist as | `Ctrl+Shift+S` |
| Close playlist | `Ctrl+Shift+Q` |
| Fullscreen | `F` |
| Leave fullscreen, or minimize | `Esc` |
| Settings | `F6` |
| About | `F1` |
| Quit | `Q` |
| Rename cell title and color (slated for removal) | `F4` |

## Mouse

| Mouse | Does |
| --- | --- |
| Drag a cell | Move it to another place (drop on a cell to swap) |
| Middle-drag | Move the picture within its cell |
| `Ctrl`+drag | Zoom into the area drawn |
| Hold `Shift` while dropping | The other drop action |
| Side buttons | Nothing by default; assign them on the Shortcuts page. They keep working with mouse clicks disabled. |

## Changed from upstream GridPlayer

- `[` `]` `\` set and clear loops (upstream: seek).
- `,` `.` `/` zoom.
- `M` mutes or unmutes every cell.
- `Esc` leaves fullscreen first.
- `E` is Keep; `K` / `J` are audio delay; `Shift+L` toggles Loop This File;
  `L` opens the List window.

## No default key

Many menu items have no key but can be given one: Stop (this cell), Mute /
Unmute (this cell), Random Loop, Loop Chapter, chapters and bookmarks, Files
to Play, Include Subfolders, Other Orientation, When Finished choices,
Leave the List, Zoom to Selection, Rotate Videos to Fit Cells, Copy File Path
/ Name / URL, Show in Folder, Open in Browser, Add Folder, Minimize,
Shortcuts and more. Find them on the Shortcuts page.
