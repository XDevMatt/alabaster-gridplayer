# Changelog

## Alabaster 0.2beta (from GridPlayer 0.5.5)

- **Pictures as slides.** jpg, jpeg, jpe, jfif, png, webp, gif, bmp, tif and
  tiff play for a set Slide duration (1-3600 s, default 10), then the cell's
  When Finished runs. See [Pictures](user-guide/pictures.md).
- **Files to Play** per cell and for `[ALL]`: images and videos, videos only,
  or images only. Defaults to Videos only; dropped pictures are still taken.
- **Aspect filter** default in Settings and the playlist, and `[ALL]` choices.
- **Snapshots** load onto the cells still there instead of crashing, with a
  "Snapshot applied to N of M cells" warning.
- Tests for snapshots, the aspect filter default, pictures and Files to Play.
- NOTICE updated for the 0.2beta changes.

## 0.5.5-alabaster.1 (first Alabaster changes)

Changes from upstream GridPlayer, as listed in `NOTICE`:

- Subtitle files (.srt, .ass, .ssa, .vtt) dropped on a cell attach to its video.
- `Shift+L` toggles Loop This File; `[` and `]` set loop start / end.
- Per-cell profiles saved with the playlist under stable cell ids.
- Aspect filter per cell.
- Browser cookies for yt-dlp on the Cookies page; the stored cookie jar is removed.
- Optional SubtitleCat search from a cell (off until enabled).
- Shortcuts entry on the right-click menu.
- Security: JSON single-instance pipe, local stream proxy listener removed,
  filtered VLC options with `--no-lua`, bundled yt-dlp only, Streamlink off the default path.
- Fixes and smaller additions; see the git log.
