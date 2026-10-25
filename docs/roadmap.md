# Roadmap

What is planned for GridPlayer Alabaster, and what is ruled out. Nothing
here is a promise of a date.

## Plugins

Alabaster has a small plugin layer, and other people are welcome to write
plugins for it. SubtitleCat is the first one and is the model to copy.

### What a plugin is today

A plugin is a Python package under `gridplayer/plugins/`, listed in the
catalog in `gridplayer/plugins/__init__.py`:

```python
PluginSpec(
    id="subtitlecat",
    module="gridplayer.plugins.subtitlecat",
    setting="plugins/subtitlecat",
    kind="subtitles",
)
```

The rules it follows, which every plugin follows:

- **Off by default.** Its setting (`plugins/<id>`, default `False` in
  `gridplayer/settings.py`) is on only when the user turns it on.
- **Not imported while off.** The catalog is data: module paths, not
  imports. `gridplayer.plugins.load(id)` returns `None` while the setting is
  off, and imports the module only when it is on. Importing the package
  itself (`gridplayer/plugins/subtitlecat/__init__.py`) does no network
  work and reads no cookies; the dialog and the client are imported on the
  first click.
- **No shared state.** The host keeps no cookie jar or session for plugins
  to share. SubtitleCat reads the user's own browser cookies for one
  request and drops them.
- **Its own settings page.** The setting lives in
  `gridplayer/params/settings_fields/plugins.py`, and its page in the
  Plugins group of `gridplayer/params/settings_pages.py`.
- **Its own entry point in the UI.** SubtitleCat adds a cell action
  (`gridplayer/widgets/video_block_subtitlecat.py`) that does nothing while
  the plugin is off.
- **Tests** that show it stays unimported while off.

To write one: add the package, one `PluginSpec`, the setting with a `False`
default, its settings page, and its UI hook, following
`docs/plugins/subtitlecat-pass-1.md`.

Plugins are in-tree for now: the catalog is a fixed tuple, so a plugin ships
as a pull request, not as a file dropped into a folder. Discovering plugins
installed separately (for example Python entry points) is a later step. It
would need a signing or allowlist story first, because a plugin runs as the
user with full access.

### Streamlink: the first candidate

Streamlink is the first planned plugin, with `kind="resolver"`. Today its
resolver's code is still in `gridplayer/utils/url_resolve/resolver_streamlink.py`,
but nothing uses it: `_resolver_map()` in
`gridplayer/utils/url_resolve/url_resolve.py` lists only yt-dlp and direct
links, and it is not a catalog entry.

**Rule:** the stream relay, upstream GridPlayer's local listener that
Streamlink's HLS route (`hls_proxy`) needs, may come back only as an
opt-in plugin:

- off by default;
- turning it on shows a warning that it starts a local network listener
  (the reason Alabaster removed it) and says what it gives in exchange;
- never the default route for any link, and never turned on by an update
  or a migration.

Alabaster itself starts no listener. A Streamlink plugin without the relay
(handing VLC the URL Streamlink resolves, with its headers) does not need
the warning about the listener, but stays opt-in like every plugin.

### Native VLC modules (libvlc plugins): assessment

Could a native VLC 3 module (a `.dll`/`.so` built for VLC) be dropped into
the bundled VLC's `plugins` folder? In principle yes; in practice only
under conditions that rule it out as a user-facing plugin mechanism.

- **ABI.** libvlccore looks up a module's entry point by a versioned name,
  `"vlc_entry" MODULE_SUFFIX` (`src/modules/bank.c`), with
  `MODULE_SUFFIX "__3_0_0f"` in VLC 3.0.x's `include/vlc_plugin.h`. A module
  built against the VLC 3.0 headers loads in any 3.0.x; a VLC 4 module, or
  one from another ABI, is skipped. The suffix is not the same everywhere:
  Debian 13's VLC 3.0.24, on the test box, exports `vlc_entry__3_0_0ft64`
  (its 64-bit time ABI), so a module built for official VideoLAN builds
  does not load there, and the other way round. On Windows a module also
  has to be built with the toolchain and C runtime the VideoLAN zip uses
  (mingw-w64) and link to its `libvlccore.dll`; MSVC builds are not
  interchangeable. In short: one build per platform and per VLC flavour.
- **The plugin cache.** Alabaster starts VLC with `--no-plugins-scan`
  whenever `plugins/plugins.dat` exists (`gridplayer/vlc_player/instance.py`,
  `_is_plugin_cache_exists`). Without a scan, libvlccore knows only the
  modules listed in the cache (`bank.c`: unmatched cache entries are kept,
  the folder is not browsed), so a module dropped in later is never loaded
  until the cache is rebuilt with `vlc-cache-gen <plugins folder>`. The
  Windows build runs `vlc-cache-gen.exe` once at build time
  (`scripts/pyinstaller/build_win.sh`), and the AppImage does too
  (`scripts/appimage/build_docker.sh`). The install folder is usually not
  writable by the user (Program Files, the AppImage, the snap), so
  rebuilding the cache after install means either writing the cache
  elsewhere or turning the scan back on, which costs start-up time on
  every launch and every decoder process.
- **What is bundled.** The Windows build copies only some VLC module
  folders (`access`, `codec`, `demux`, and so on), and the Linux builds
  delete others (`scripts/_helpers/blacklist_vlc_linux.txt`, including
  `lua`, so VLC's own Lua playlist scripts do not run either). A native
  module that depends on a missing one fails quietly.
- **Safety.** A native module runs in the decoder process with the user's
  full rights and no sandbox, and the opt-in rules above cannot reach
  inside it.

Verdict: native modules are possible for a build we make ourselves (built
in CI, per platform, against the exact VLC we bundle, with the cache
rebuilt), not as something users drop in. No such module is planned.

### Upstream GridPlayer: no plugin mechanism

Upstream GridPlayer (vzhd1701/gridplayer, checked up to `342c155`,
2026-10-20) has no plugin mechanism of its own, legacy or current. Its
commits that mention "plugin" are about:

- VLC's own module cache and paths: `8311e7c` (skip the scan when the cache
  exists), `449eb97` (plugin path), `2e57211` and `55c0c88` (cache at
  build time), `c9ff21e` (more VLC modules in the Windows build);
- Streamlink and yt-dlp "plugins", meaning their site extractors:
  `PLUGIN_URLS` in `gridplayer/utils/url_resolve/static.py` is a list of
  links to those projects' supported-site pages, and `021e61a` proxied
  streams to carry the extractors' session parameters.

So there is nothing upstream to be compatible with. If upstream ever adds
one, the opt-in rules above are the condition for supporting it.

## Separate audio

See `docs/merges/fixes-20261023.md`, section 2a: what plays now (whole
manifests, plain MP4 pairs as an input slave), and what waits for the
bundled ffmpeg.

## ffmpeg and ffprobe in every build

Decided: Alabaster will bundle ffmpeg and ffprobe ("size doesn't matter,
reliability does"). The plan is in section 2a of
`docs/merges/fixes-20261023.md`.

## Next iteration

Planned for the next round, not built yet.

### Truncated-file stall cap

A truncated or partly downloaded file stalls for 10 to 14 s after it
starts (VLC restarts it again and again, about 2.5 s a cycle), so "Video
initialization timeout" (`player/video_init_timeout`, default 120) never
fires. Fix: in `PlayerBase.cb_end_reached`, if the pass was "waiting it
out" and the time never moved past the previous freeze point, fail with
"Video stopped unexpectedly" instead of restarting. Test:
`tests/test_player_base.py::test_a_stall_waited_out_twice_is_an_error`.
Deferred by the maintainer on 10-24-2026.
Built, merged from `stall-fix-20261024` (`33b016a`).

### Per-cell stats overlay (spec v2)

From the maintainer, 10-24-2026.

1. Primary fields, first and largest: video codec and resolution.
2. A processing line: the video processing active on that cell
   (deinterlacing on or off and its mode, aspect or crop override, zoom,
   color and video adjustments, speed); "none" when nothing is applied.
3. Secondary: frame rate, audio codec and channels, current bitrate,
   frames decoded, displayed and dropped.
4. mpv-style keys: one flashes the stats on the cell under the mouse for a
   few seconds, another toggles them on. Check for clashes with the
   existing shortcuts first.
5. A per-cell right-click toggle too.
6. Out of scope: live graphs, a global stats panel.

### Full path in the cell title

Approved by the maintainer, 10-24-2026. A settings option "Show full path in cell
title", off by default. Local files only; narrow cells keep eliding in the
middle, with the whole path in a tooltip. Links and yt-dlp titles stay as
they are. Hook: `VideoBlock._default_title` / `Video.uri_name`.

Built, merged from `full-path-title-20261024` (commit `0cee133`). Known
limitation, verified by the maintainer on Windows 10-25-2026: no tooltip over hardware
video cells. Workaround: single mode. Not being pursued.

### Restore order before Randomize

The List window's Randomize (the button beside Sort, Sort > Randomize, or
Randomize List, Ctrl+Shift+N, on a list cell) puts a list in a random order
once, the item playing first, to be played straight down. Source Order only
restores a list read from a folder or a link. Keep the order from just
before Randomize, and add a "Restore order before Randomize" entry to the
Sort menu (like Randomize / Restore in MPC-HC's playlist). It brings back an
order built by hand too, blocks added by hand included. Picking the next
item at random as it plays is Shuffle ("When Finished" > Play Random File),
a different thing.

### Skip audio-only files

Folder and list playback include audio files (opus, mp3 and so on), which
show a placeholder cell in a video wall. Add an option to skip audio-only
files in folder and list playback, off by default.

### Keep a Copy of a stream (release item, built in)

Required for the first release. Built in, not a plugin: it reuses the
bundled yt-dlp that already plays the link, so there is nothing to keep
off by default.

A cell action, "Keep a Copy", for a link (a URL played through yt-dlp).
It saves the playing video to a folder with the bundled yt-dlp, in the
background, so playback is not interrupted. A note on the cell says when
the copy is done, or why it failed. The folder is a setting, asked for the
first time. Local files do not show the action. A copy is permanent, not a
cache, so the app never deletes it.

### Window to video size

Requested by the maintainer, 10-25-2026. Not built yet. Size the window to the
current video's own resolution, like MPC-HC: Alt+1 for 50%, Alt+2 for
100% and Alt+3 for 200%. Single mode only. With two or more videos
showing, it changes nothing and a short note says it works in single
mode. The size is the picture area, so the
window frame and any bars are added on top. It leaves a maximized or
full-screen window as it is, and keeps the window on the screen it is on,
shrinking to fit when the video is larger than that screen. Check the keys
against the current keymap before binding them.

### Reset all settings

Requested by the maintainer, 10-25-2026. Not built yet. Today each changed setting
has its own reset button, and each settings page has a "Reset" button that
resets that page only. Add "Reset all settings…" in the Settings window, as
a menu option on the page Reset button, not on the About page. It always
asks first, naming that every page goes back to its defaults. Only app
settings are reset: playlists, lists, bookmarks and the keymap are left
alone unless a later task says otherwise.

### Reset the view on the next file (release item)

Reported by the maintainer, 10-25-2026: zoom sticking between videos is unexpected.
Today a cell that moves to another file (Play Next File, next or previous
in a folder or list, Shuffle) resets only the position, the A-B loop, the
audio and subtitle files added by hand, and the title; everything else
stays with the cell (`VideoBlockNavigation.switch_to`). Change it so zoom,
pan and crop go back to the defaults for each new file. Speed, volume,
aspect ratio, and the audio and subtitle delays still carry over. A
setting, on by default, "Reset zoom, pan and crop on the next file",
turns this off for anyone who wants the old way. A list's own crop shape
(`_keep_list_shape`) still applies to its items. Reloading or seeking in
the same file does not reset anything.
