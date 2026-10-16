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
