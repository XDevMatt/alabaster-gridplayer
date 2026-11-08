# Plugins and streaming

This page explains how GridPlayer Alabaster opens web links, how it uses your
browser's cookies, how it plays streams whose audio and video come
separately, what SponsorBlock does, and how the opt-in plugin layer and the
SubtitleCat.com plugin work.

## How a link is opened

When you add a link (Add URL(s), paste, drop, or a list item), Alabaster
**resolves** it into something VLC can play, then hands the result to VLC.

Three resolvers can do this:

| Resolver | What it is |
| --- | --- |
| **yt-dlp** | The yt-dlp Python module bundled with Alabaster, or a yt-dlp program you choose. Reads thousands of sites, YouTube included. |
| **Streamlink** | The Streamlink Python module bundled with Alabaster. Mainly for live streams. |
| **Direct** | No resolver: the link is given to VLC as it is. |

Settings, Streaming, Link Resolution:

- **Priority URL resolver** (default **yt-dlp**): which resolver tries first.
  The others follow if it cannot handle the link. YouTube links always use
  yt-dlp.
- **Resolver priority patterns**: a table of URL patterns (wildcard host,
  wildcard URL, or regular expression) that pick a different resolver for
  matching links.
- **Use Streamlink for HLS streams when possible** (on by default): live HLS
  streams that Streamlink can open are fetched through Streamlink. With it
  off, and for recorded HLS, VLC opens the stream itself. (The setting's
  tooltip mentions "the player's own HLS proxy"; in Alabaster that proxy is
  never started, so VLC opens those streams directly.)
- Links with schemes VLC handles natively (`rtsp`, `rtmp`, `mms`, `udp` and
  similar) go straight to VLC.

### Using your own yt-dlp

Sites change often, and an old yt-dlp stops working on them. The bundled
module is only as new as the Alabaster build.

To use a yt-dlp you keep up to date:

1. Install it: `winget install yt-dlp.yt-dlp` (or `choco install yt-dlp`).
2. In **External yt-dlp**, enter the full path to `yt-dlp.exe`, or just
   `yt-dlp` to use the one on your PATH.
3. Update it with `winget upgrade yt-dlp.yt-dlp` or `yt-dlp -U`.

Empty, or a program that cannot be found, means the built-in module. The
external program is used to resolve links. **Test a YouTube link** and the
browser list on the Cookies page still use the built-in module.

### JavaScript runtime (Deno) for YouTube

YouTube scrambles many stream addresses with a script that yt-dlp has to run.
Alabaster does not bundle an engine for this.

- Install Deno: `winget install DenoLand.Deno`, then restart Alabaster.
- By default Alabaster uses **Deno only**: from the folder in **JavaScript
  runtime**, otherwise from your PATH.
- **Allow JavaScript engines found on PATH** (off by default) also allows
  Node (22 or newer), QuickJS (`qjs`) and Bun, and looks on PATH, in the data
  folder and in the installers' home folders. It is off by default because a
  binary in those places could be replaced by another program.
- **Test a YouTube link** reports which engine will be used and where it is.

Not every YouTube link needs an engine. Install one when YouTube links start
failing.

## Browser cookies

Some links play only when you are signed in. YouTube in particular may answer
"Sign in to confirm you're not a bot".

Alabaster lets yt-dlp read the cookies of a browser you are signed in with,
the same as yt-dlp's `--cookies-from-browser` option.

1. Open Settings, Streaming, **Cookies**.
2. Choose the **Browser**: Firefox, Chrome, Edge, Brave, Chromium, Opera,
   Vivaldi, Safari or Whale (the list shows the browsers this yt-dlp can
   read).
3. Optionally enter a **Profile** name or path. Empty uses the browser's most
   recently used profile.

How it behaves:

- Cookies are read from the browser **each time a link is resolved** and kept
  in memory for that request only.
- Alabaster **does not import, store or export cookies**. There is no cookie
  jar. A leftover `cookies.txt` in the data folder from an older build is not
  read and not deleted.
- Cookies go to yt-dlp only. Streamlink, SponsorBlock and the "is this link
  supported" check get none.
- The SubtitleCat.com plugin reads the same browser's cookies for
  `subtitlecat.com`, per request, in memory only.

Caveats:

- Reading cookies depends on yt-dlp and on the browser. On Windows, recent
  Chrome and Edge versions protect their cookie store, and yt-dlp may fail to
  read it, especially while the browser is running. Firefox is usually the
  most reliable choice. If reading fails, the link fails to resolve; the log
  says why.
- You must actually be signed in to the site in that browser and profile.
- Sites can block or rate-limit an account or address that fetches a lot of
  streams. Using your account's cookies ties that traffic to your account.
- Some links still fail with cookies, because a site blocks the request for
  other reasons (region, age, DRM, or the site changed and yt-dlp needs an
  update).

## Network settings

Settings, Streaming, Network:

| Setting | What it does |
| --- | --- |
| **Proxy** | **System** (default) uses Windows' proxy settings. **None** connects directly. **Custom** uses **Proxy address**, for example `http://host:port` or `socks5h://host:port`. |
| **Request timeout** | How long to wait for a site while opening a link. Auto (0) leaves each library its own default. Does not affect playback. |
| **User agent** | How Alabaster identifies itself. Empty uses a current desktop Chrome user agent. A link that comes with its own user agent keeps it. |
| **Force IPv4** | Connect over IPv4 only. Try it if links stall or a site blocks your IPv6 address. |
| **Verify TLS certificates** | On by default. Turn off only for a proxy that signs traffic with its own certificate. |
| **Allow http links in https playlists** | On by default. Some IPTV streams need it. |
| **Test network** | Runs connection checks and shows a report you can copy. |

What they apply to:

- Resolving links (yt-dlp, Streamlink), downloading lists and thumbnails,
  SponsorBlock lookups, SubtitleCat.com requests, and streams that yt-dlp
  feeds to VLC in-process (see below) follow all of these settings.
- **Playback by VLC itself follows only the user agent.** VLC uses Windows'
  proxy settings on its own and has no IPv4-only or certificate option.
  Upstream GridPlayer routed such links through a local relay server;
  Alabaster removed that listener, so it does not do this. If you need
  playback proxied too, set the proxy for the whole computer.

## Stream quality, separate audio, HLS and DASH

Many sites serve video and audio as separate streams. Alabaster plays these
in VLC **without merging them first** and without a local server:

| Stream kind | How it plays |
| --- | --- |
| A stream with video and audio together | VLC plays it directly. |
| **HLS master playlist** or **DASH manifest** whose video and audio share one manifest | The whole manifest goes to VLC, which pairs video and audio itself. The **Stream Quality** menu caps the quality VLC chooses, and the **Audio Track** menu switches audio language. |
| A plain (non-fragmented) **MP4 video** with its own **M4A** audio file | VLC plays the video with the audio file attached as an input slave. Seeking works. |
| Links VLC cannot fetch itself (they need browser impersonation or extra headers) | yt-dlp fetches the bytes inside Alabaster and feeds them to VLC through callbacks. |
| Video whose audio is only available as a separate **fragmented** MP4 or WebM file (YouTube's DASH formats among them) | **Not supported yet.** Alabaster offers only the formats it can play with sound. Pairing these needs ffmpeg and is planned. |

In practice this means some YouTube videos are offered at lower qualities
than the site shows, because the higher ones exist only as separate DASH
files.

**Stream Quality** on the cell menu (and the default in Settings, New
Videos, Streaming Videos):

- **Auto (fit to pane)**: picks the quality that fits the cell, and changes it
  when the cell keeps a new size for **Adapt after** seconds (default 15).
- **Best** (default), **Audio Only**, or a fixed resolution (2160p, 1440p,
  1080p, 720p and so on, with 60 fps variants).

Other streaming options (New Videos, Streaming Videos, and the cell menu):
**On network error** (Show error / Reload a few times (3) / Keep reloading),
**Auto reload time** for live streams (0 = never), and **Reload** (`F5`).

AES-128 encrypted HLS plays. DRM-protected streams do not.

## SponsorBlock

Settings, Streaming, SponsorBlock. Off by default.

When on, every YouTube video you play is checked on
[SponsorBlock](https://sponsor.ajay.app/). Only a short prefix of a hash of
the video ID is sent. For each category you choose **Skip**, **Show in seek
bar**, or **Disabled**:

| Category | Default |
| --- | --- |
| Sponsor | Skip |
| Unpaid/Self Promotion | Show in seek bar |
| Interaction Reminder | Show in seek bar |
| Intermission/Intro Animation | Disabled |
| Endcards/Credits | Disabled |
| Preview/Recap | Disabled |
| Hook/Greetings | Disabled |
| Filler Tangent | Disabled |
| Non-Music Section | Disabled |
| Highlight | Show in seek bar (cannot be skipped) |

SponsorBlock data is by Ajay Ramachandran and contributors, licensed CC
BY-NC-SA 4.0.

## The plugin layer

Alabaster has an opt-in plugin layer:

- A plugin is a package under `gridplayer/plugins/` with one entry in the
  catalog in `gridplayer/plugins/__init__.py`.
- Every plugin is **off by default** and has a setting on the **Plugins** page
  of Settings.
- A plugin's code is **not even imported** until its setting is on.
- The host shares no cookie jar or session with plugins.
- SubtitleCat.com is the only plugin today. Streamlink is still built in, not
  a plugin.

Plugins from others are welcome; SubtitleCat.com is the model to follow.

## SubtitleCat.com plugin

[SubtitleCat.com](https://www.subtitlecat.com/) is a third-party subtitle site.
GridPlayer Alabaster is not affiliated with or endorsed by it. Alabaster
bundles no SubtitleCat.com account, key, cookies or subtitle content.

### Turn it on

1. Settings, Plugins, SubtitleCat.com: tick **Enable SubtitleCat.com**.
2. Optional: tick **Request translations** to allow asking the site to
   translate a subtitle.
3. Every request uses your own signed-in session. Sign in to subtitlecat.com
   in a browser (the **Sign in** and **Sign up** buttons open the site in your
   default browser), and choose that browser on Settings, Streaming,
   **Cookies**. Without a signed-in session, requests stop with a message
   asking you to sign in.

### Use it

1. Right-click a cell with a video, **Subtitles > Find subtitles on
   SubtitleCat.com…**. Opening the window does not contact the site.
2. The search box is filled from the video's name. Edit it and click
   **Search**.
3. Pick a result and click **Show languages**.
4. Pick a language and click **Download**. The subtitle is saved and attached
   to the cell right away.
5. For a language that has no file yet, **Translate** (when enabled) asks the
   site to make one. It sends one request per click and never retries. The
   site's answer, including a limit or VIP message, is shown as sent. When a
   translation is ready, click **Download**.

Details:

- Each button is one request, with a minimum gap between requests.
- The file is saved next to the video when that folder can be written,
  otherwise in the `subtitles` folder of the data folder. The bytes are
  written as received.
- The plugin follows the Network settings.
- With the plugin off, the menu item is hidden and no plugin code runs.

## What is not supported

- Merging separate fragmented audio and video (needs ffmpeg; planned).
- Streams protected by DRM.
- A stored cookie file. Use the browser setting instead.
- Upstream's local stream relay. It may only come back as an opt-in plugin,
  off by default, with a warning.
