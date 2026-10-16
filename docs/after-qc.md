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
