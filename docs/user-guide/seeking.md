# Seeking, chapters, bookmarks and sync

Keys act on the cell under the pointer. With `Shift` (or `Alt` for the
percent jumps) they act on every cell. Everything is also on the right-click
menu under **Playback > Jump (to)**.

## Jump

| Do | This cell | Every cell |
| --- | --- | --- |
| Jump to 0%, 10%, ... 90% | `0` ... `9` | `Alt+0` ... `Alt+9` |
| Jump to a time | `T` | `Shift+T` |
| Jump somewhere random | `R` | `Shift+R` |
| +1% / -1% | `Right` / `Left` | `Shift+Right` / `Shift+Left` |
| +10% / -10% | `'` / `;` | `Shift+'` / `Shift+;` |
| Short step (5 s) | `Ctrl+Right` / `Ctrl+Left` | `Ctrl+Shift+Right` / `Ctrl+Shift+Left` |
| Medium step (15 s) | `Ctrl+]` / `Ctrl+[` | `Ctrl+Shift+]` / `Ctrl+Shift+[` |
| Long step (30 s) | `Ctrl+'` / `Ctrl+;` | `Ctrl+Shift+'` / `Ctrl+Shift+;` |
| Next / previous frame | `S` / `D` | `Shift+S` / `Shift+D` |

+5% and -5% are on the menu with no key. The step lengths are in Settings,
Defaults, Playlist, Step Sizes.

!!! note "Changed from upstream"
    In upstream GridPlayer `[` and `]` seek. In Alabaster they set loop points;
    see [Loops](loops.md).

## Speed

| Do | This cell | Every cell |
| --- | --- | --- |
| Faster | `C` | `Shift+C` |
| Slower | `X` | `Shift+X` |
| Normal | `Z` | `Shift+Z` |

Steps of 0.05x, from 0.2x to 12x.

## Chapters

**Playback > Chapters**: Previous Chapter, Next Chapter, and the chapter
list, for files that have chapters. **Loop Chapter** is under Loop.

## Bookmarks

**Playback > Bookmarks**: **Add Bookmark**, Previous / Next Bookmark, the
list, and **Manage Bookmarks…**. Bookmarks are saved with the playlist.
With **Share bookmarks between cells with the same file** on (default),
cells playing the same file share its bookmarks and they stay when a cell
closes. **Playlist Settings > Bookmarks in Playlist…** lists them all.

## Sync

Right-click, **Sync** (the whole grid):

- **Seek**: Disabled (default), **Sync By Percent** (seek the others to the
  same share of their length) or **Sync By Timecode** (to the same time).
- **Play / Pause**: pausing one pauses all.
- **Speed**: changing one's speed changes all.
- **Zoom and Position**.

**Sync Others** on a cell's menu does it once: seek the others by percent or
timecode, or copy zoom and position.

## SponsorBlock (YouTube)

Settings, Streaming, SponsorBlock (off by default) skips or marks sponsor
and similar segments that viewers have tagged on YouTube videos. Only a
short prefix of a hash of the video id is sent.
