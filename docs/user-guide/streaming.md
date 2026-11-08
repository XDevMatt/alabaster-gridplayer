# Streaming

A cell can play a link instead of a file: YouTube and the other sites
[yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md),
the sites [Streamlink](https://streamlink.github.io/plugins.html) supports,
HLS (`.m3u8`) and DASH streams, IPTV lists, and plain `http`, `https`,
`rtsp`, `rtmp` links that VLC opens itself.

## Add a link

- **Add > Add URL(s)** (`Ctrl+U`): paste one or more links.
- **Add > From Clipboard** (`Ctrl+V`).
- Drag a link from your browser onto the window.
- Pass links on the [command line](window.md#command-line).

A link to a playlist or channel (a YouTube playlist, a web M3U) becomes a
[list](lists.md) in one cell.

## What's built in, and what you may need

The yt-dlp and Streamlink Python modules are inside the app; nothing else
is needed for most links.

| You want | You need |
| --- | --- |
| Most sites, live streams, IPTV | Nothing extra |
| YouTube, when links start failing | [Deno](https://deno.com/), see [JavaScript runtime](#javascript-runtime-deno) |
| A yt-dlp you update yourself | `yt-dlp.exe`, see [External yt-dlp](#external-yt-dlp) |
| Videos that need a login, or YouTube's "confirm you're not a bot" | A browser you're signed in with, see [Cookies](#cookies) |

ffmpeg and ffprobe aren't used yet; see [Separate audio](#separate-audio).

## Cookies

Settings, Streaming, **Cookies**: pick the **Browser** you're signed in with
(Firefox, Chrome, Edge, Brave, Chromium, Opera, Vivaldi, Whale; the list
shows the browsers yt-dlp can read) and, if needed, a **Profile**. Empty
profile means the browser's most recently used one.

yt-dlp then reads that browser's cookies when it opens a link, the same as
`--cookies-from-browser`. Cookies are read at that moment and kept in memory
only: Alabaster doesn't import, store or export them, and a leftover
`cookies.txt` in the data folder isn't read.

If yt-dlp can't read a Chromium-based browser's cookies while that browser
is open, close it and try again. That's a yt-dlp and browser limit, not an
Alabaster setting.

## JavaScript runtime (Deno)

YouTube scrambles its stream addresses with a script that has to be run.
Deno isn't bundled. If YouTube links stop playing:

1. Install Deno (`winget install DenoLand.Deno` or `choco install deno`).
2. Restart Alabaster.
3. Settings, Streaming, Link Resolution, **Test a YouTube link** shows the
   engine that will be used and where it is.

By default Alabaster uses only Deno, from the **JavaScript runtime** folder
if you set one, else from `PATH`. Turn on **Allow JavaScript engines found
on PATH** to also use Node (22+), QuickJS (`qjs`) or Bun, and look in the
data folder and the installers' home folders too. Off is safer: a binary
on `PATH` can be replaced by another program.

## External yt-dlp

The built-in yt-dlp module is updated only when Alabaster is. To use a
yt-dlp you keep updated yourself (`winget install yt-dlp.yt-dlp`, `choco
install yt-dlp`, then `yt-dlp -U` now and then):

- Settings, Streaming, Link Resolution, **External yt-dlp**: the full path to
  `yt-dlp.exe`, or just `yt-dlp` for the one on `PATH`.
- Empty, or not found: the built-in module.
- The external program resolves links. The checkups and the cookie browser
  list still use the built-in module.

## Which tool opens a link

Settings, Streaming, Link Resolution:

- **Priority URL resolver**: **yt-dlp** (default), **Streamlink** or
  **Direct** (straight to VLC) tries first; the others follow if it can't.
  YouTube always uses yt-dlp.
- **Resolver priority patterns**: a table of URL patterns (wildcard host,
  wildcard URL or regex) and the resolver each one should use.
- **Use Streamlink for HLS streams when possible** (on): live HLS streams
  that Streamlink can open are fetched by Streamlink.

## HLS and separate audio

- **HLS and DASH manifests** go to VLC whole. VLC pairs the video with its
  sound, the **Stream Quality** menu caps the height VLC picks (VLC can still
  step down on a slow network), and **Audio > Audio Track** switches
  language without a reload.
- **A plain MP4 video with its own M4A sound file** plays with the sound as a
  second input, and can be seeked.
- Alabaster starts **no local server or relay** for any of this.

### Separate audio

Other streams whose sound comes separately, YouTube's DASH files among them,
can't be paired by VLC. Merging them needs ffmpeg, and that merge isn't
built yet; it's what ffmpeg and ffprobe are reserved for. Until then, a
link of that kind may not play the way you expect. Try another **Stream
Quality**, or a format the site offers with sound built in.

## Per-cell stream options

On a cell playing a link:

- **Stream Quality**: Best (default), a fixed height, **Audio Only**, or
  **Auto (fit to pane)**, which changes quality to fit the cell after it
  has kept its size for **Adapt after** seconds (default 15).
- **Reload** (`F5`, `Shift+F5` for all) and **Auto Reload** (live streams
  only, every N minutes; 0 = never).
- **On Network Error**: Show Error, **Reload a Few Times** (default, 3
  attempts) or Keep Reloading.
- **URL**: Copy URL, Copy URL at Current Time (where the site supports a
  time in the link), Open in Browser.

## Network

Settings, Streaming, **Network**: **Proxy** (System, None, or Custom with an
address such as `http://host:port` or `socks5h://host:port`), **Request
timeout** while a link opens, **User agent**, **Force IPv4**, **Verify TLS
certificates**, and **Allow http links in https playlists**. They apply to
`http` and `https` links; other kinds (`rtsp`, `rtmp`) are opened by VLC and
only the user agent reaches them.

## SponsorBlock

Settings, Streaming, SponsorBlock: skip or mark sponsor and similar
segments on YouTube videos. Off by default. See [Seeking](seeking.md#sponsorblock-youtube).

## When a link won't play

1. Try it in a browser: is it still there?
2. YouTube: set [Cookies](#cookies), install [Deno](#javascript-runtime-deno),
   run **Test a YouTube link**.
3. Try an [external yt-dlp](#external-yt-dlp) you've just updated.
4. Raise **Video initialization timeout** (Settings, General, Player,
   Timeouts; default 120 s) for slow streams.
5. Settings, Advanced, Logging: set **Log level** to Debug and check the log
   in the [data folder](../reference/data-folder.md).
