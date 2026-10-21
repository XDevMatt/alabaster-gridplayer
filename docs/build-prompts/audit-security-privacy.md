# Build prompt: security and privacy audit (GridPlayer Alabaster)

## Your role: you are the expert, so let it rip
You're the expert here: superoptimizer, bug stomper and security hardener. The owner and his earlier assistant have already reviewed this code, and they assume they missed things. Your job is to find what they overlooked. Everything listed below is a floor, not a ceiling: the known findings, the measurements and the checks are where you start, not the scope. Add your own checks, challenge our assumptions and findings, and report anything you think matters, including areas we never mentioned. The only fixed limits are the owner's hard requirements and the report-first rule. If your report shows gaps, the owner will point you at specific targets in a follow-up.

Owner: XDevMatt. Phase 1 is a findings report only. Do not change code until the owner approves the report.

## Hard requirements (non-negotiable)
1. **Stealth on every port.** Until the app itself sends a request, nothing it runs may be reachable: no listening TCP or UDP socket on any interface, including 127.0.0.1 and ::1. No accept, no RST, no banner, nothing that reveals a host. Only replies to connections the app opened are allowed.
2. **No network traffic unless the owner asks for it.** Opening a stream URL counts as asking, for that stream only. No update checks, telemetry, crash upload, favicon, thumbnail or metadata fetches, DNS prefetch or connectivity probes at startup or idle.
3. **No stored cookies; fresh browser cookies at request time are fine.** The app must never keep its own cookie jar: no cookies.txt, no cache, no "allow update" write-back, no cookie values in settings or logs. Old stored cookies replayed while another process on the same host is using newer ones is exactly the kind of reveal to avoid. Keep the request-time path: when a stream is opened, yt-dlp may read the current cookies straight from the owner's chosen browser (`--cookies-from-browser`, the `cookies/from_browser` and `cookies/browser_profile` settings), use them for that request only, and keep them only in memory. Remove the stored-jar parts (`gridplayer/utils/cookies.py` jar and import/export, `CookieStoreList`, `cookies/allow_update`, cookie-file handling) and keep or simplify the from-browser option.4. **Minimum metadata when streaming.** Send only what the site needs. Review User-Agent, Referer, Accept-Language and any headers in `gridplayer/utils/network.py`; no local paths, usernames or hostnames in any request.

## Known findings to confirm and plan fixes for
- `gridplayer/utils/stream_proxy/` runs a `ThreadingHTTPServer` on `127.0.0.1:<random>` so VLC can pull streams. That violates rule 1. Propose a replacement with no listener (for example, hand VLC the direct URL with the needed options, or feed it through a pipe or libVLC media callbacks).
- Single-instance pipe `\\.\pipe\gridplayer-alabaster-fileopen` (`gridplayer/utils/single_instance.py`, Python `multiprocessing.connection` AF_PIPE). Verify it rejects remote clients (`PIPE_REJECT_REMOTE_CLIENTS`) and is reachable only by the same user. Any local process can currently push file paths into it; decide whether to validate what it accepts.
- `gridplayer/utils/network_checkup.py` makes test connections. It must run only when the owner opens the checkup on purpose, never automatically.
- `gridplayer/utils/url_resolve/` (yt-dlp, Streamlink): list every outbound request they can make, and whether any run without a user action.

## Exploit-surface review
- Media parsing lives in libVLC and ffmpeg. Report the bundled versions and known CVEs against them, and which demuxers or modules load. Recommend pinning, and disabling modules the player doesn't need. Do not hand-audit ffmpeg.
- The app's own parsers: `.gpls` playlists (legacy `#GRIDPLAYER` and the JSON format), `.m3u`, dropped URLs and paths, and file-open pipe input. Look for path traversal, unbounded reads, and pickle or eval-like loading.
- Anything that runs a subprocess or shell command with user-controlled text.

## Privacy trail on disk
List everything written outside the media folders: settings.ini, logs (do any log full URLs, tokens or titles?), media_shapes.json, screenshots, recent files, caches. Say what each reveals and propose a retention or off switch.

## Verification required with the fix phase
- Add an automated test that starts the app offscreen, plays a local file, and fails if the process ever opens a listening socket (check with `psutil.Process().net_connections()` or the Windows `GetExtendedTcpTable`/`GetExtendedUdpTable` APIs).
- Add a test that fails on any outbound connection during startup and local playback.

## Deliverable
`docs/audit/security-privacy-findings.md`: each finding with file and line, severity, how it was confirmed, and the proposed fix. Stop there and wait for approval.
## Owner direction: yt-dlp first, Streamlink parked for a plugin system
Optimize streaming for yt-dlp as the only built-in resolver. Streamlink is not being axed; it is going back in the oven as a candidate first plugin once a plugin architecture exists.
- Today Streamlink is the first-choice resolver (`streaming/resolver_priority` = STREAMLINK), the stream proxy is built on it, and thumbnails, checkups and `http_in_playlists.py` import it. Move all of that to yt-dlp: VLC gets the direct media URL plus any required headers as libVLC media options, with no proxy or listener.
- Keep Streamlink code out of the default build path, but don't destroy the design knowledge: note in the report which parts would make a clean plugin later (its resolver class and HLS handling).
- List any stream type that stops working without Streamlink (for example, HLS that needs per-segment headers or keys, Twitch or Kick live edge cases) and how yt-dlp handles it, so the owner can decide. Both Twitch and Kick serve HLS (Kick runs on Amazon IVS). yt-dlp has extractors for both, but Kick answers 403 unless requests are impersonated (yt-dlp `--impersonate chrome` via curl_cffi) on the manifest and every segment, see yt-dlp/yt-dlp#14444. If that means VLC can't fetch segments directly, say so and propose a fix that still opens no listener.
- Retest the upstream live and m3u8 bugs with yt-dlp only: vzhd1701/gridplayer #320 (live broadcasts), #239 (m3u8 links), #309 (live HLS crash), #160 (streamlink.webbrowser).

## Later, not now (design notes only, no code)
Keep the plugin interface in mind so these could slot in later without a rewrite. Do not build any of them in this pass:
- Streamlink as a resolver plugin.
- A subtitle-search plugin, for example SubtitleCat (subtitlecat.com). It makes network calls only when the owner asks for subtitles. Owner notes: free SubtitleCat accounts get one download per day (per the owner); he signs up through a real browser, and the plugin may present a Chrome User-Agent and TLS fingerprint. For its login, prefer the same request-time approach (read the current SubtitleCat cookie from the owner's browser when a subtitle is requested, keep it in memory only) over storing one. Anything it must keep stays inside that plugin, opt-in, never shared with the core app or other plugins.
- A media analyzer plugin using local ffprobe or MediaInfo. It flags items yellow or red in the list before playback when the codec, resolution, bit depth or bitrate is likely too heavy for this hardware (Intel Iris Plus with Quick Sync). It stays fully local.
