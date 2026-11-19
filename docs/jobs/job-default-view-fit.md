# Job: default view mode Fit

Owner decision (2026-11-18): a fresh install, or a portable folder on
default settings, opens videos in **Fit** view, not Fill.

Start from `main`. One step, one commit, progress note in
`docs/progress/job-default-view-fit.md`.

## Change

- `gridplayer/settings.py`: `"video_defaults/cell_view_mode"` default
  `VideoCellViewMode.FILL` -> `VideoCellViewMode.FIT`.
- Do not touch the legacy migration (`LEGACY_VIEW_MODES`,
  `_migrate_aspect_to_cell_view_mode`, `models/video.py` loader). Saved
  settings and playlists that already name a view mode keep it.

## Tests

- `tests/test_settings_reset.py`: reset assertions that expect `FILL`
  now expect `FIT`. The test that picks a non-default value (around
  line 328, currently `FIT`) must pick `FILL` or `STRETCH` instead so it
  still writes a key.
- Add a regression test: with empty settings,
  `settings.get("video_defaults/cell_view_mode") is VideoCellViewMode.FIT`;
  a playlist or settings file that stores `Fill` still loads as Fill.
- Full suite green.

## Out of scope

Any other default, menu wording, or migration behaviour.
