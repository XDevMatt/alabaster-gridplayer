# Engine: keep VLC, port to mpv, or mpv Lua grid?

## Recommendation
Keep libVLC now. Do T4/T7/T6/T2 on VLC. Plan mpv as a second video
driver (not a rewrite) once T3 works, built by a stronger agent. Do not
rebuild the grid as mpv Lua scripts.

## Criteria
| | VLC (now) | libmpv (python-mpv) | mpv + Lua grid |
|---|---|---|---|
| 4-9 videos stable | Proven here; process pool (`multiprocess/process_manager.py`, Videos per process) isolates crashes | Good, but one handle per cell in-process; would need the same process pool | One mpv window; grid via `--lavfi-complex` stacks = one graph, one failure stops all |
| HW decode per instance (QSV/d3d11va) | Hardware driver; decoder choice is per instance | `hwdec=d3d11va`/`qsv` per handle; `d3d11va-copy` when filters are needed | Not per cell inside a lavfi grid |
| Subtitles | Works (T1); harmless avcodec warning | libass, `sub-add` per handle, best in class | Fine |
| Scaling (T7) | swscale is per instance and ignored by HW; per-cell needs our own SW path (see after-qc) | Per handle: `scale=ewa_lanczossharp`, `dscale=mitchell`, separate up/down, on GPU, works with HW decode | One scaler for the whole grid |
| Deband (T7) | `gradfun` filter, pulls HW frames to CPU | `deband=yes` built in, GPU | Built in |
| Port effort | 0 | 25 modules import vlc (`vlc_player/*` 10, `widgets/video_frame_vlc_*` 5, `widgets/video_block*` 4, `managers/active_block.py`, `managers/video_driver.py`, `utils/item_info.py`, `utils/libvlc*.py`). Most sit behind `vlc_player/video_driver_base*.py` + `widgets/video_frame_*`, so a new mpv frame + driver is weeks, not months | Rewrite of the whole app (playlists, menus, overlays, shuffle, layout); not worth it |

## Why mpv later
T7 wants per-cell up/downscale and deband that also work with hardware
decode. VLC 3 cannot do that per cell; mpv does it with options. If
picture quality becomes the main pain, an mpv driver is the fix.
