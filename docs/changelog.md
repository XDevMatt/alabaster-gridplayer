# Changelog

## Alabaster 0.2beta (from GridPlayer 0.5.5)

- **Pictures as slides.** jpg, jpeg, jpe, jfif, png, webp, gif, bmp, tif and
  tiff play for a set Slide duration (1-3600 s, default 10), then the cell's
  When Finished runs. See [Pictures](user-guide/pictures.md).
- **Files to Play** per cell and for `[ALL]`: images and videos, videos only,
  or images only. Defaults to Videos only; dropped pictures are still taken.
- **Rotate to fit** (optional, in Settings): turn a video so it matches its
  cell and uses more of the screen. A landscape video in a cell taller than
  wide stands up; a portrait video in a cell wider than tall lies down. You
  pick the turn direction (90 clockwise or 270 counter-clockwise). A
  transform picked from the menu still wins for that file.
- **Aspect filter**: skip files whose orientation does not match the cell
  (Skip it), with a default in Settings and the playlist, and `[ALL]`
  choices. Play it and Ask are the other options.
- **Snapshots** load onto the cells still there instead of crashing, with a
  "Snapshot applied to N of M cells" warning.
- Tests for snapshots, the aspect filter default, pictures and Files to Play.
- NOTICE updated for the 0.2beta changes.

## 0.5.5-alabaster.1 (first Alabaster changes)

Changes from upstream GridPlayer, as listed in `NOTICE`:

- Subtitle files (.srt, .ass, .ssa, .vtt) dropped on a cell attach to its video.
- `Shift+L` toggles Loop This File; `[` and `]` set loop start / end.
- Per-cell profiles saved with the playlist under stable cell ids.
- Rotate videos to fit their cells (optional), so more of the cell is picture.
- Aspect filter per cell: skip files of the other orientation (Skip it), or ask.
- Browser cookies for yt-dlp on the Cookies page; the stored cookie jar is removed.
- Optional SubtitleCat.com search from a cell (off until enabled).
- Shortcuts entry on the right-click menu.
- Security: JSON single-instance pipe, local stream proxy listener removed,
  filtered VLC options with `--no-lua`, bundled yt-dlp only, Streamlink off the default path.
- Fixes and smaller additions; see the git log.
