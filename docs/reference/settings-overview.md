# Settings overview

`F6` or right-click, **Settings**. Pointing at a setting shows what it does.
The dialog has a search box. Every setting, with its default, range and key,
is in the [full settings list](settings.md).

**Defaults** pages are what new playlists and new cells start with.
Right-click, **Playlist Settings > Edit Playlist Settings…** shows the same
pages for the open playlist only.

## The ones most people change

| Want to | Setting | Default |
| --- | --- | --- |
| Hear new cells | Defaults, New Videos, Audio, **Muted** | On (muted) |
| Change the volume step | General, Player, **Volume step per wheel notch or key press** | 3% |
| Stop new cells looping | Defaults, New Videos, Playback, **When finished** | Loop this file |
| Include audio or pictures from folders | Defaults, New Videos, Playback, **Files to play** | Videos only |
| Not read subfolders | Defaults, New Videos, Playback, **Include subfolders** | On |
| Skip the other orientation | Defaults, New Videos, Playback, **Other orientation** | Play it |
| Rotate videos to fit | General, Player, **Rotate videos to fit their cells** | Off |
| Show the whole picture | Defaults, New Videos, Video, **View mode** | Fill |
| Ask before closing unsaved | Defaults, Playlist, Saving / Restoring, **Unsaved changes on close** | Discard Changes |
| Remember positions | Defaults, Playlist, Saving / Restoring, **Save videos playback position** | Off |
| One cell for everything dropped | Defaults, Playlist, Drag-n-Drop, **Cells** | One per item |
| Random repeats files open elsewhere | Defaults, Playlist, Folder Navigation, **Skip files open in other cells** | On |
| Change keys | General, **Shortcuts** | |
| Subtitles from SubtitleCat.com | Plugins, SubtitleCat.com | Off |
| YouTube login | Streaming, Cookies, **Browser** | Off |
| Your own yt-dlp | Streaming, Link Resolution, **External yt-dlp** | Built-in |

!!! warning "Unsaved changes are discarded by default"
    Closing the app or opening another playlist never stops to ask, unless
    you change **Unsaved changes on close** to Ask or an Auto Save choice.
    Save with `Ctrl+S` first.

## Pages

- **General: Player**: color scheme, one instance, stay on top, start
  maximized / fullscreen, screensaver, media keys, rotate to fit, volume
  step, tray, history, timeouts, memory, cache, screenshots.
- **General: Subtitle Style**, **Shortcuts**, **Language**.
- **Defaults: Playlist**: saving / restoring, playback, step sizes, folder
  navigation, sync, input, overlay, grid, drag-n-drop, lists.
- **Defaults: New Videos**: overlay color, audio, subtitles, video,
  playback, streaming videos.
- **Streaming**: Link Resolution, SponsorBlock, Cookies, Network.
- **Plugins**: SubtitleCat.com.
- **Advanced**: Video Decoder, Logging.

Settings are saved in `settings.ini`; see [Data folder and portable mode](data-folder.md).
