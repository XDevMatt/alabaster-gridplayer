# After QC

Do not build any of this during the current code freeze. Sysop is testing
what is already in the tree. Pick this up only after that QC is done.

Two features are in scope for the pass after QC: picture quality on the
Video Decoder page, and two loop keys in the style of mpv.

## Picture quality

The Video Decoder page has no banding filter and no choice of scale
algorithm. Both belong on that page as real controls. The free-form VLC
options box stays, and anything typed there still wins, because those
options are appended last in `InstanceVLC.init_options`.

### Banding filter

Add a deband control, off by default, with a strength the page can set.

libVLC 3 can do this with the `gradfun` video filter
(`--video-filter=gradfun`, radius and strength in the filter options).
That runs on the decoded frame, so it cleans bands that are already in
the source. It does not clean bands that the scaler adds afterwards.

A video filter on the hardware driver pulls frames back to the CPU.
Say so on the page. Software and Software SP can run it in place.
Hardware and Hardware SP should either refuse it with that reason, or
accept the cost. Do not hide the fallback.

The transform filter already sets `--video-filter` for a rotated or
flipped video (`get_vlc_options`). A second `--video-filter` from the
free-form box replaces that chain. The new control has to join
`gradfun` onto the existing chain, not emit a second option that drops
the transform.

### Scale algorithms, above and below 100%

100% means one source pixel to one pane pixel. It does not mean
GridPlayer's view scale of 1.0. Scale 1.0 is "fit the picture in the
cell" (`ViewParams.scale`). A 4K clip fitted into a small cell is
already far under 100% while scale is still 1.0. Zooming in with `+`
raises scale and can cross 100%.

`calc_crop_region` / `ViewPlacement` already know the source rectangle
in frame pixels and the target rectangle in pane pixels. Compare those.
The limiting axis decides:

- target larger than source: upscale algorithm
- target smaller than source: downscale algorithm
- equal: no scaler choice matters

Each cell can be on a different side of 100% at the same time, and one
cell crosses the line when it is zoomed or the grid is rearranged.
`--swscale-mode` is one value for a whole VLC instance, so it cannot
be the mechanism. The software picture path
(`SoftwareVideoSurface` / the RGB frames from the software driver) is
where a per-cell choice can run. The hardware driver presents with
Direct3D or the platform GPU output, which scales on its own and
ignores swscale. The page should offer the two algorithms and say
which driver honors them.

Algorithms worth listing, mapped from libswscale:

- Upscale default: Lanczos. Also offer Bicubic, Spline, Bilinear, Nearest.
- Downscale default: Area. Also offer Bicubic, Lanczos, Bilinear, Nearest.

Nearest is the pixel-art choice and stays off unless picked. Area is
the one that keeps a grid of shrunk videos from shimmering. Lanczos is
the one that keeps a zoomed-in picture sharp without the blocks of
bilinear.

Changing the pair should apply to pictures already on screen. It is a
present-time choice, not an instance option, so it must not force a
reload the way `misc/vlc_options` does.

## Loop keys

A-B is already usable on the fly. Loop This File is not.

Set Loop Start is `,`, Set Loop End is `.`, Loop Reset is `/`. They
sit on the Loop submenu and on keys. A single `l` that cycles start,
end, then clear is only a shorter way to press those three. It is
optional. The hole is the other loop.

Loop This File, Play Next File, Play Previous File, and Play Random
File live under When Finished. None of them has a key. Each is a
menu choice that sets one end action. Binding "Loop This File" in
the shortcut editor would only turn that mode on. It would not
return the cell to the next-file or shuffle action it had before.
That return is what has to be one key.

### `l` — A-B marks, optional

One command, three presses, on the active cell. The three commands
above keep their own keys.

1. Set the loop start to the current time (`LoopControl.set_start`).
2. Set the loop end to the current time (`LoopControl.set_end`).
3. Clear both (`LoopControl.reset`).

Pressing again starts the cycle over. A press that would put the end
at or before the start does nothing, which `set_end_time` already
enforces.

While either mark is set, the cell already repeats that stretch and
does not run When Finished (`VideoBlock.loop_end_action` seeks back
when `loop_start` or `loop_end` is set). Clearing the marks returns
the cell to its When Finished action. `l` does not change that action.

### `Shift+L` — loop this file, or go on as before

A per-cell toggle over the end action.

- On: set `end_action` to `VideoEndAction.LOOP_FILE` and remember the
  action it replaced.
- Off: put the remembered action back.

The remembered action is that cell's own When Finished choice: Play
Next File, Play Random File (shuffle from the original folder), Play
Previous File, pause, stop, or close. A cell that was already on Loop
This File when the toggle is first used has nothing to restore; use
the playlist default for that field.

The toggle does not clear A-B marks. Marks still take priority, the
same way they do now. `Shift+L` matters once the marks are clear, and
it decides whether the file repeats or the cell steps on.

Save the remembered action with the video, next to `end_action`, so a
saved playlist restores both the toggle and what it goes back to.

## Specs v2 (from the maintainer, 2026-10-16). QC unfrozen for this work.

Order: T4, T7, T6, T5, T2, T3. Do one task per session. Each task ends
with its acceptance test passing and a local commit. Tag per task:
[GB] = Grok Build can do it. [STRONG] = needs a stronger agent.

### T1 subtitles - DONE (milestone 1, commit f206758)
Drop of .srt/.ass/.ssa/.vtt on a cell attaches it
(`DragNDropManager._drop_subtitles`). The VLC log line "avcodec:
refusing to decode non validated subtitle codec" cannot be removed in
VLC 3 (no option exists, hardcoded) and is harmless: VLC falls back to
subsdec/libass. Do not try to fix it.

### T4 per-cell loop toggle + MPC-HC [ ] keys [GB]
Goal: `Shift+L` toggles the active cell between `VideoEndAction.LOOP_FILE`
and the end action it had before; `[` = Set Loop Start, `]` = Set Loop End
(extra keys; `,` `.` `/` stay).
Files: `gridplayer/models/video.py` (`Video`: add
`end_action_before_loop: VideoEndAction | None = None`),
`gridplayer/widgets/video_block.py` (`VideoBlock.set_end_action`, add
`toggle_loop_file`), `gridplayer/params/actions.py` (new "Toggle Loop File"
action, `"func": ("active", "toggle_loop_file")`, key `Shift+L`; add `[` and
`]` as second keys of "Set Loop Start"/"Set Loop End"),
`gridplayer/widgets/video_block_loop.py` (`LoopControl`, no change expected).
Rule: while A-B marks are set they stay in charge.
Accept: new `tests/real_app/scenarios/loop_toggle.py`: set Shuffle, press
toggle -> end_action LOOP_FILE; press again -> SHUFFLE_FILE; save/reload
playlist keeps it. `python -m tests.real_app.run loop_toggle` -> PASSED.

### T7 stable cell IDs + per-cell profile [GB, careful]
Goal: each cell has a stable id and a profile saved with the playlist;
app settings are defaults, the cell overrides only what it sets.
Files: `gridplayer/models/video.py` (`Video.id` already a UUID4 - keep it
stable across save/load and shuffle; do not regenerate on load),
new `gridplayer/models/cell_profile.py` (`CellProfile`: `sources:
list[CellSource]` (path, weight=1.0), `upscale`, `downscale`, `deband`,
`end_action`, `loop` - all `| None`, None = use app default),
`gridplayer/models/playlist.py` (`Playlist`: add
`cell_profiles: dict[UUID, CellProfile]`; old playlists must still load),
`gridplayer/settings.py` (defaults only). Scaler/deband fields only store
the choice; applying them is the "Picture quality" section above.
Accept: unit test `tests/test_cell_profile.py`: round-trip a playlist
with 2 profiles; old playlist without the key loads; `None` fields fall
back to settings. `pytest tests/test_cell_profile.py --basetemp=%TEMP%\gp_pytest`.

### T6 per-cell source folders, weights, no repeats [GB]
Goal: shuffle picks from the cell's `CellProfile.sources`; folder chosen
by weight first, then a file inside it (so folder size does not decide
how often it plays); a per-cell recent-history window (80% of pool, max
500) blocks repeats.
Files: new `gridplayer/utils/cell_pool.py` (`CellPool.pick(rng) -> Path`,
pure Python, no Qt), `gridplayer/widgets/video_block_navigation.py`
(`NavigationControl.shuffle` uses `CellPool` when the cell has sources).
Accept: `tests/test_cell_pool.py`: seeded rng, 2 folders (3 and 300
files, weight 1 each) -> each folder ~50% over 1000 picks; no repeat
inside the window.

### T5 lookahead queue + scan cache [STRONG]
Goal: per cell, keep a queue of next files with cached duration+aspect.
Buckets: short <30s, medium 30s-5min, long >5min, weighted random mix.
Short clips go only to cells whose current aspect class already fits,
never trigger reflow. Layout changes rate-limited (max one per 3 min).
If two cells near end together, schedule the aspect change then; else
swap in a later queued file that fits.
Files: `gridplayer/utils/item_info.py` (already probes with its own
`vlc.Instance`; reuse for duration/size), new
`gridplayer/utils/media_scan_cache.py` (json cache in app data dir,
key = path+mtime+size), new `gridplayer/utils/cell_queue.py`.
Accept: unit tests with fake scan data for bucket mix, short-clip rule,
rate limit.

### T2 allowed aspect combos [GB]
Goal: pure function `is_allowed(portrait:int, landscape:int) -> bool`.
Allowed (4K screen): 3 or 4 portrait (0 landscape); 1-4 landscape (0
portrait); 2 landscape + 2 portrait. Everything else disallowed (e.g.
3L+1P, 1L+3P).
Files: new `gridplayer/utils/layout/aspect_rules.py`; aspect class =
portrait if width<height after rotation.
Accept: `tests/test_aspect_rules.py` table test of all combos 0..4.

### T3 geometry-aware shuffle + reflow [STRONG]
Goal: each cell shuffles alone. Before loading the next file, check
`is_allowed` with its aspect. If not allowed: the cell holds (loops
current video as T4 loop), shows a small dot + countdown = remaining
time of the cell that ends first; when it ends, reflow and load.
Reflow example from 4L: 2 landscapes stacked in the centre, 2 portraits
full-height on left and right.
Files: `gridplayer/player/managers/grid.py` (`GridManager._layout`,
`_adjust_grid_stretch` - today all stretch is 1), `gridplayer/utils/layout/`,
`gridplayer/widgets/video_block_navigation.py`,
`gridplayer/widgets/video_overlay_elements.py` (dot+countdown).
Accept: real_app scenario with 4 landscape cells + a portrait in one
cell's pool -> cell holds, countdown shown, reflow to 2L+2P layout.

### T8 stepwise orientation reflow [split: T8-1 GB, T8-2 STRONG or GB with care]
Priority: after T8a, before T2/T3 remainder, T6, T5 (the maintainer, 2026-10-16).

Goal: 4 cells. When a cell finishes and its next shuffled file has the
other orientation, the grid moves one step:
4L <-> 3L+1P <-> 2L+2P <-> 1L+3P <-> 4P. One cell changes orientation per
finish event, so the portrait count changes by exactly 1: the layout is
just a function of WHICH cells are portrait. No hold, countdown or
lookahead (that is T3/T5).

Stock GridPlayer has no mixed-orientation layout (only cell count and
rows/cols first). This adds an explicit per-cell-rect mode, like
FancyZones: rects on a weighted grid with spans. Pure 4L/4P reuse the
existing grid (FIXED 2x2 / 1x4).

What exists (looked up):
- Placement: `GridManager._render_video_grid` -> `_populate_fixed` /
  `_populate_flow` (gridplayer/player/managers/grid.py) put blocks into a
  `QGridLayout` with span 1x1; `_adjust_grid_stretch` sets every row and
  column stretch to 1; `adapt_grid` calls it. `GridMode` (params/static.py)
  = AUTO_ROWS, AUTO_COLS, FIXED. Order: `utils/layout/flow_layout.py`
  (`FlowLayout`), `utils/layout/grid_layout.py` (`GridLayout`).
- Aspect: the driver emits `video_dimensions_changed(w, h)`
  (vlc_player/video_driver_base.py); `video_frame_vlc_base.py`
  `set_track_dimensions` stores it in `media.video_tracks[*].video_dimensions`.
  Rotation is `Video.transform` (90/270 swap w/h).
- End hook: `VideoBlock.loop_end_action` -> `_step_at_end` ->
  `NavigationControl.shuffle` (SHUFFLE_FILE). The new file's size is
  known only after it opens -> reflow on the dimensions signal, not on EOF.
Missing: per-cell orientation, row/col spans, non-equal stretch, a
trigger from a cell to the grid.

Layout on 3840x2160 (stretch weights in px; Qt scales them to any screen).
Each cell keeps the app aspect "fit": video letterboxed inside its rect.
| State | Columns (stretch) | Rows | Cells (row, col, rowspan, colspan) | Picture in rect |
|---|---|---|---|---|
| 4L | 1920,1920 | 1080,1080 | L (0,0) (0,1) (1,0) (1,1) | 1920x1080 exact |
| 3L+1P | 1080,1380,1380 | 1080,1080 | P (0,0,2,1); L (0,1) (0,2); L (1,1,1,2) | P 1080x1920 (60px bars); top L 1380x776; bottom L 1920x1080 in 2760x1080 (pillarbox) |
| 2L+2P | 1080,1680,1080 | 1080,1080 | P (0,0,2,1) (0,2,2,1); L (0,1) (1,1) | P 1080x1920; L 1680x945 |
| 1L+3P | 1080,1680,1080 | 1080,1080 | P (0,0,2,1) (0,2,2,1); L (0,1); P (1,1) | P 1080x1920; L 1680x945; centre-bottom P 607x1080 (transitional, ugly by design) |
| 4P | 960 x4 | 2160 | P (0,0) (0,1) (0,2) (0,3) | 960x1707 (226px bars) |
Which cell goes where: keep each cell in the slot closest to where it
was (portraits fill edge slots first: left, then right, then
centre-bottom), so one step moves as few cells as possible.

T8-1 pure layout function [GB]
1. New gridplayer/utils/layout/orientation_layout.py:
   `def orientation_layout(cells: list[tuple[str, bool]], previous: dict[str, tuple] | None = None)`
   -> `OrientationLayout(col_stretch: list[int], row_stretch: list[int], places: dict[str, tuple[int,int,int,int]])`.
   `cells` = (video id, is_portrait) for exactly 4 cells; return None for any
   other count. Use the table above. `previous` = last places, to keep cells
   where they were.
2. `def is_portrait(width, height, transform) -> bool` in the same file
   (swap for 90/270 rotation; square = landscape).
3. tests/test_orientation_layout.py: each of the 5 states gives the table
   rects; every cell placed once; no overlap; one portrait flip moves at
   most 2 cells; 3 cells -> None.

T8-2 wiring [STRONG, or GB with care]
4. gridplayer/params/static.py `GridMode`: add `ORIENTATION = auto()`; menu
   entry next to the other grid modes (gridplayer/params/actions.py /
   menu.py, copy how FIXED is offered).
5. grid.py `GridManager`: in `_render_video_grid`, when mode is ORIENTATION
   and there are exactly 4 blocks, call new `_populate_orientation()` that
   uses `orientation_layout` and `self._grid.addWidget(vb, r, c, rs, cs)`,
   and in `adapt_grid` set the stretches from the result instead of
   `_adjust_grid_stretch`. Otherwise fall back to the existing flow code.
6. Trigger: when a block's video dimensions arrive (connect in the block to
   `video_dimensions_changed`), if its orientation flipped, ask the grid to
   `reload_video_grid()` (through `self._ctx.commands`, the way other
   blocks ask the grid; do not add a global).
7. tests/real_app/media.py: add a short portrait test clip (generated by
   ffmpeg like the others; test media only). New scenario
   tests/real_app/scenarios/orientation_reflow.py: 4 landscape cells,
   open the portrait clip in one -> grid is 3L+1P with that cell
   full-height left; repeat -> 2L+2P.

Acceptance: `pytest tests/test_orientation_layout.py` passes;
`python -m tests.real_app.run orientation_reflow` PASSED; `tracks`,
`loop_toggle`, `subtitle_drop` still PASSED.

### T8a aspect filter (fallback, do FIRST) [GB]
Goal: Shuffle (and Next) in a cell skip files whose orientation does not
match the cell's current video (portrait vs landscape), so the grid never
needs to change. Off unless turned on per cell; no layout code.

What exists: `FolderNavigator._take_step` (gridplayer/utils/folder_navigator.py)
calls `ShuffleBag.next(avoid=..., exists=Path.is_file)`
(gridplayer/utils/next_file.py); `exists` is already a per-file predicate,
so a shape check can ride on it. Next uses `FolderScan.existing_neighbour`.
`utils/item_info.py` already parses files with its own `vlc.Instance`
(`_length_of`); a shape probe is the same code reading the video track
width/height instead of duration.

Steps:
1. gridplayer/utils/item_info.py: add `shape_of(path) -> bool | None`
   (True = portrait, None = unknown), copying `_length_of` and reading the
   first video track size (`media.tracks()` / `get_tracks_info`); apply
   rotation via `is_portrait` from T8-1 (or a local copy: swap for 90/270).
   Cache results in a dict keyed by (path, mtime, size). Timeout per file
   = FILE_PARSE_TIMEOUT_MS.
2. gridplayer/utils/folder_navigator.py `FolderNavigator`: accept an
   optional `want_portrait: Callable[[], bool | None]` (given by
   `NavigationControl` in gridplayer/widgets/video_block_navigation.py from
   the block's current track dimensions + `Video.transform`). In
   `_take_step`, for RANDOM pass
   `exists=lambda p: p.is_file() and _shape_ok(p)`; for NEXT step the
   neighbour forward until one fits. Unknown shape (None) counts as a fit.
3. Budget: probe at most 10 candidates or 1.5 s per step, then take the
   next file anyway (never get stuck, never loop forever).
4. Toggle: `Video.is_aspect_filter: bool = False` (models/video.py) and a
   check-able action "Keep Orientation" in params/actions.py next to
   "Toggle Loop File" (no default key). Saved with the playlist for free.
5. Tests: tests/test_aspect_filter.py with a fake `shape_of` (monkeypatch):
   bag of 6 files, 3 portrait -> 20 random steps from a portrait current
   only return portrait; all wrong shape -> still returns a file after the
   budget; unknown counts as fit. Real app: run `navigation`, `tracks`,
   `loop_toggle` - all PASSED.

Feasibility: Grok Build-sized (about 150 lines + tests, one place in the
step code). Risk: probing runs on the GUI thread; with 10 probes a slow
disk can stall a cell switch up to 1.5 s. Acceptable for a first version;
T5's scan cache removes it later.