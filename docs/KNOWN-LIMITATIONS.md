# Known limitations

This page lists what GridPlayer Alabaster does not do, and behavior that is
known to be rough. Read it before reporting a problem.

## Platform and distribution

- **Windows only.** Alabaster is built and tested on Windows 10 and 11
  (64-bit). The source still contains upstream GridPlayer's macOS and Linux
  code and build recipes, but this project does not test, package or support
  macOS or Linux. Anyone may port it from the source under the GPL.
- **No macOS or Linux packages** come from this project. Flathub, Snap,
  AppImage and DMG packages named GridPlayer are upstream GridPlayer.
- **Not on PyPI.** `pip install gridplayer` and `uv tool install gridplayer`
  install upstream GridPlayer.
- **Release candidate only.** The portable zip is out as prerelease
  [v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1). It is not code-signed, so Windows SmartScreen may
  warn. The installer and Chocolatey package are not released yet.
- **Installer next to upstream GridPlayer.** The installer recipe has its
  own installer id, install folder (`C:\Program Files\GridPlayer Alabaster\`),
  Start menu folder and file-type registrations, so a build made from it
  installs and uninstalls without touching an installed upstream GridPlayer.
  No installer has been built or published from it yet.
- **Languages.** The Language page and the translations come from upstream.
  Text added by Alabaster is English only, and Alabaster does not maintain
  translations.
- Some names still say "GridPlayer": the program file `GridPlayer.exe`, the
  log file `gridplayer.log`, the tray name and notifications, the Windows
  taskbar app id, and the file-association ids. The About window shows the
  version as `0.5.5-alabaster.1`.

## Playback and performance

- **GPU contention.** When two hardware-decoding players share one integrated
  GPU (for example Alabaster next to another player, or very many hardware
  cells), they compete for it. Cells may stutter or turn grey. Try **Videos
  per process** = 1, Hardware SP, or Software decoding for one of them.
- **Grey panes on Next.** In a grid, pressing Next now repaints only the cell
  that moves on. On Windows a pane may still go grey for a moment, because the
  old player is released on the interface thread and can take up to 5 seconds.
  Try **Videos per process** = 1 first.
- **Ogg/Opus loops.** When an Ogg or Opus file loops, VLC may write repeated
  "seek to 0%" lines to the log. Playback is not affected.
- **Rotate to fit reopens the video** to turn it, so the picture blinks once.
- Too many cells at once can freeze the app; that is why Alabaster warns above
  12 cells.

## Streaming

- **Separate fragmented audio** (YouTube's DASH formats among them) is not
  supported. Those qualities are not offered.
- **Network settings and VLC.** Proxy, Force IPv4 and Verify TLS apply to
  link resolution, lists, thumbnails, SponsorBlock, SubtitleCat.com and
  in-process streams, but not to what VLC fetches itself. VLC follows only the
  user agent and uses Windows' proxy settings. Upstream's local relay was
  removed.
- The tooltip of **Use Streamlink for HLS streams when possible** mentions "the
  player's own HLS proxy". That proxy is never started in Alabaster; VLC opens
  those streams itself.
- **Browser cookies** depend on yt-dlp being able to read the browser. Recent
  Chrome and Edge on Windows can block this, especially while running. Firefox
  is usually more reliable. Streamlink receives no cookies.
- Sites block, rate-limit or change often. Keep an external yt-dlp updated if
  links stop working.
- DRM-protected streams do not play.

## Features with known gaps

- **Other orientation: Ask** has not been re-verified recently. **Skip it** is
  the supported mode. The filter checks at most 10 files per step and uses the
  cell's live shape, so resizing can change what fits.
- **Keep (`E`)** works only in single mode on a local file, always copies,
  shows nothing on screen (the result is in the log), and has no options.
- **Rename (`F4`)** changes only the title shown in the app, not the file. A
  custom title can stay after Next, Previous or Random until a restart or
  playlist load. It is marked for removal unless a use is found.
- **Per-cell profiles** store fields for sources, scaling filters, deband,
  end action and loop, but only the aspect filter is used. The others have no
  effect and no interface.
- **Shuffle On Load** is off by default, but a playlist saved while it was on
  keeps its own value until you untick it and save the playlist again.
- Cells from an Explorer multi-select arrive in the order the hand-offs reach
  the window, not Explorer's order.
- Over hardware-decoded cells there is no tooltip, so a long full path in a
  narrow cell is cut; use single mode to read it.

## Privacy

- Alabaster sends no telemetry. The crash dialog shows the error (which may
  include local file paths) with a Copy button and a link to the issue page;
  nothing is sent unless you send it.
- Network requests happen only for links you open, lists and thumbnails you
  load, the checks you run from Settings,
  SponsorBlock (when on), and SubtitleCat.com (when on and you click).
