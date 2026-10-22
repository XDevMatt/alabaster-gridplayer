# Security and privacy findings — GridPlayer Alabaster

Phase 1 report only. No code was changed. Owner: XDevMatt.

Confirmed against the tree as of this audit (source read, Python 3.12.10 `multiprocessing.connection` inspected, VideoLAN SB-VLC-3024 and yt-dlp/Kick #14444 checked on the web, upstream issues #320/#239/#309/#160 pulled from the GitHub API). Live streams were not played; #320/#239 need a yt-dlp-only playback pass in the fix phase.

Severity: **Critical** (code execution), **High** (hard-requirement break, credentials, local RCE), **Medium** (privacy, extra network, DoS), **Low** (banner, defense in depth), **Info** (design note).

---

## Assumptions challenged

1. **“The proxy is localhost, so it is fine.”** Rule 1 forbids a listener on 127.0.0.1. Any local user can SYN the port and get a Python HTTP banner. With a leaked `session_id` the proxy is an authenticated-by-obscurity open relay that fetches with the session’s cookies.
2. **“The file-open pipe only accepts paths.”** `client.recv()` unpickles first. A crafted pickle is process-equivalent to the player, then the list-of-paths check never runs.
3. **“VLC can be handed the URL plus headers.”** libVLC 3 only honours `:http-user-agent` and `:http-referrer`. Cookies, extra headers, TLS impersonation, proxy-off, and IPv4-only are why the proxy exists. Kick (and anything with `impersonate` on the format) cannot be fetched by VLC at all.
4. **“Live HLS already bypasses the proxy.”** `streaming/hls_via_streamlink` leaves the protocol as `"hls"`, but `video_block_stream.py` only skips the proxy for `"direct"`. Live HLS still starts `ThreadingHTTPServer`.
5. **“Network checkup might run by itself.”** It does not. Only the Settings buttons start it.
6. **“Stored cookies are off unless imported.”** `cookies/enabled` and `cookies/allow_update` default to **True**. An existing `cookies.txt` is sent and merged back.
7. **“Python named pipes reject remote clients.”** On this machine’s 3.12.10 they do not set `PIPE_REJECT_REMOTE_CLIENTS`. There is also no `authkey`.

---

## F1. Stream proxy is a localhost HTTP listener (rule 1)

**Severity:** High  
**Where:** `gridplayer/utils/stream_proxy/server.py:73` (`StreamProxyServer(ThreadingHTTPServer)`), `stream_proxy.py:18-25` (`("127.0.0.1", 0)` then `serve_forever`), `player/managers/stream_proxy.py:17-23` (started on first `add_stream`).  
**Confirmed:** `TCPServer.__init__` binds and listens in the constructor, before `serve_forever`. `video_block_stream.py:344-351` sends every non-`direct` stream through `add_stream`, including live `"hls"`.  
**What it does:** Random port on 127.0.0.1. No auth. `BaseHTTPRequestHandler` answers with `Server: BaseHTTP/0.6 Python/3.12.x`. Simple streams put the upstream URL in the query string (`server.py:132-136`). `do_GET` (`server.py:525-553`) will fetch any `url`+`protocol` that carries a valid `session_id` (`server.py:619-624`). DASH `urljoin(base_url, tail)` (`server.py:183-208`) can replace the host if `tail` is absolute.  
**Proposed fix:** Remove the proxy from the default path.

- **Simple HTTP(S)** that only needs UA/Referer: pass the CDN URL to libVLC with `:http-user-agent` / `:http-referrer` (`player_base.py:135-137`, `_http_header_options` at `1856-1871`). This is already `"direct"`.
- **Cookies, extra headers, signed HLS, DASH fragments:** do not open a socket. Feed VLC with `libvlc_media_new_callbacks` (`vlc_player/vlc.py:986-1013`, libVLC 3.0+). The read callback pulls from yt-dlp’s downloader / `curl_cffi` session in-process.
- **Live HLS/DASH that VLC can follow itself:** hand VLC the manifest URL as `"direct"` so VLC’s adaptive demuxer stays on the live edge (this is also the #320 fix).
- **Kick / `impersonate` formats:** VLC’s TLS fingerprint is not Chrome. Keep fetching in yt-dlp/`curl_cffi` and only give VLC bytes. Do not skip those formats (`resolver_yt_dlp.py:229-243`).

Do not replace the HTTP server with another TCP/UDP listener (including a SOCKS helper or a second localhost port).

---

## F2. Single-instance pipe: pickle RCE, no auth, no remote reject (rule 1 adjacent)

**Severity:** Critical (same-user RCE); High (remote named-pipe if SMB is open)  
**Where:** `gridplayer/utils/single_instance.py:16` (`\\.\pipe\gridplayer-alabaster-fileopen`), `:53` `connection.Listener(S_NAME, S_TYPE)` with no `authkey`, `:101-105` `listener.accept()` then `client.recv()`, `:127-134` `_send_data` via `connection.Client`, `:193` `AllowSetForegroundWindow(-1)`.  
**Confirmed:** Python 3.12.10 `PipeListener._new_handle` creates the pipe as `PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT` and a NULL DACL. **`PIPE_REJECT_REMOTE_CLIENTS` is not set.** `recv()` uses pickle (`ForkingPickler`). `_handle_input_data` (`:114-124`) only checks `isinstance(input_data, list)` *after* unpickle. The list is emitted as files/URLs with no scheme or path check. Linux: `$XDG_RUNTIME_DIR/gridplayer/…socket` with no chmod; parent `XDG_RUNTIME_DIR` is typically 0700 so it stays same-user.  
**Proposed fix:**

- Stop using `multiprocessing.connection` for this. Length-prefixed UTF-8 JSON (a list of strings) over a raw Windows named pipe / AF_UNIX socket.
- Windows: `PIPE_REJECT_REMOTE_CLIENTS`, `FILE_FLAG_FIRST_PIPE_INSTANCE`, a DACL for the current user only.
- Linux: `chmod 0o600` on the socket, `0o700` on the directory.
- Reject anything that is not a list of strings; cap count and length; allow only existing local files, `.gpls`, and `URL_ALLOWED_SCHEMES`.
- Optional HMAC with a per-install key in the data dir, so a random local process cannot open URLs that cause outbound fetches.
- Replace `AllowSetForegroundWindow(ASFW_ANY)` with the second instance’s PID only.

The pipe is not TCP/UDP, so the owner’s “stealth on every port” test will not see it. Treat it as a separate local IPC test.

---

## F3. Stored cookie jar (rule 3)

**Severity:** High (credentials on disk, replay of stale logins)  
**Where:** `gridplayer/utils/cookies.py` (whole module: `COOKIE_FILE_NAME = "cookies.txt"`, `CookieStore` at `:179`, `cookie_store()` at `:297` under `%APPDATA%\vzhd1701\GridPlayer-Alabaster\cookies.txt`), `ytdl_cookies()` `:436-464` (buffer merge when `cookies/allow_update`), `settings.py:217-218` defaults **`cookies/enabled`: True**, **`cookies/allow_update`: True**. UI: `resources/ui/settings_dialog.ui` / `CookieStoreList`, `dialogs/settings.py:255-256, 1237-1253`. Streamlink gets the stored jar only (`cookies.py:355-377`); browser cookies are yt-dlp-only (`browser_cookie_opts` `:397-411`).  
**Confirmed:** File mode 0o600. Values are not logged. Settings OK rewrites the file. `allow_update` merges yt-dlp’s jar back, which is the stale-replay case the owner named.  
**Proposed fix:** Delete the stored-jar path: `CookieStore`, import/export, `CookieStoreList`, `cookies/allow_update`, `cookies/enabled` as a jar switch, `cookiefile` in `ytdl_cookies`. Keep `cookies/from_browser` + `cookies/browser_profile` as yt-dlp `cookiesfrombrowser=(name, profile or None, None, None)`, in memory for that resolve only. If a leftover `cookies.txt` exists, delete it on first run after the change (or refuse to start until the owner removes it). Do not log or write cookie values.

---

## F4. `misc/vlc_options` can open a VLC listener (rule 1)

**Severity:** High  
**Where:** `settings.py:186` `"misc/vlc_options": ""`, `vlc_player/instance.py:338-360` `_iter_settings_options` feeds every `--…` token from settings into `libvlc_new`, last so it wins.  
**Confirmed:** Nothing blocks `--http-port`, `--extraintf=http`, `--sout=#http{…}`, `--telnet-port`, SRT listener, etc. `--no-lua` is set earlier (`instance.py:138`) and would normally kill luahttp, but a later `--lua` / `--extraintf` from this setting overrides.  
**Proposed fix:** Deny-list listener and stream-out flags (`--http-port`, `--https-port`, `--rtsp-port`, `--telnet-port`, `--extraintf`, `--control`, `--sout`, `--sout-keep`, `--intf=http`). Prefer an allow-list of decoder/filter options. Document that this box cannot turn GridPlayer into a server.

---

## F5. Almost every stream starts the proxy, not only “complex” ones

**Severity:** High (makes F1 the common case)  
**Where:** `widgets/video_block_stream.py:344-351`; `resolver_yt_dlp.py:509-513`; `resolver_streamlink.py:173-176`; `resolver_base.py:118-134`.  
**Confirmed:** Only `protocol == "direct"` skips the proxy. HLS VOD → `hls_proxy`. Live HLS with `hls_via_streamlink` → `"hls"` → still proxied. Plain `http` → proxied. `needs_relay` is true if cookies match, proxy is not SYSTEM, IPv4 is forced, or TLS verify is off (`network.py:171-182`).  
**Proposed fix:** With F1: default to `"direct"` + libVLC header options. Use media callbacks only when VLC cannot fetch (cookies beyond UA/Referer, impersonation, AES keys that need extra headers). Drop `streaming/hls_via_streamlink` from the default path.

---

## F6. Kick (and other impersonation) formats are dropped, and VLC cannot fetch them

**Severity:** High for Kick playback after Streamlink is parked  
**Where:** `resolver_yt_dlp.py:229-243`, `_needs_impersonation` `:530-540`. yt-dlp/yt-dlp#14444: Kick (Amazon IVS HLS) returns 403 unless `--impersonate chrome` via `curl_cffi` on the manifest **and every segment**.  
**Confirmed:** GridPlayer already skips formats with `impersonate` set, because neither VLC nor the Streamlink-based proxy impersonates TLS. `pyproject.toml` depends on `yt-dlp[default,curl-cffi]`; the 32-bit Windows build strips curl-cffi (`scripts/pyinstaller/build_win.sh:26-32`). Locked yt-dlp is 2026.8.19.  
**Proposed fix:** For impersonation formats, never give VLC the URL. Resolve with yt-dlp `impersonate` enabled, download segments with `curl_cffi`, feed bytes through `libvlc_media_new_callbacks`. 64-bit Windows/Linux/macOS keep curl-cffi. 32-bit Windows: Kick stays unsupported; say so. Do not add a TLS-impersonating localhost proxy.

---

## F7. Network checkup is user-triggered only (known item, confirmed OK)

**Severity:** Info (no bug)  
**Where:** `dialogs/settings.py:666, 716-727` (`networkTestButton` → `NetworkCheckup`); `utils/network_checkup.py:43` `TEST_URL = "https://www.youtube.com/robots.txt"`; YouTube checkup `dialogs/settings.py:664, 687-714`, `ytdlp_checkup.py:50-52` (Blender video + `https://www.youtube.com/`).  
**Confirmed:** No import of these modules from `main/` or player startup. Checkup dialog starts a thread only when shown (`dialogs/checkup.py:89, 204`). No cookies on the network checkup (`network_checkup.py:15-16`).  
**Proposed fix:** Keep as-is. Do not auto-run. After Streamlink is parked, rewrite `fetch_capped` / YouTube checkup to yt-dlp/`requests` so Streamlink is not imported from Settings.

---

## F8. Outbound requests from resolvers (known item)

**Severity:** Medium where they run without a distinct user action; Info where they are the stream the owner opened

Nothing in `main/` imports Streamlink or yt-dlp. `url_resolve.py:43-45` delays both until a URL is resolved.

| Trigger | What goes out | User asked? |
|---|---|---|
| Open a stream/page URL | yt-dlp `extract_info` (webpage, player JS from the site, APIs, nsig). Streamlink plugin HTTP if it is tried first. `stream_detect` extra GET/HEAD (`stream_detect.py:42-123`) | Yes, that URL |
| YouTube URL | yt-dlp only (`url_resolve.py:294-296, 328-347`) | Yes |
| `is_able_to_handle` | Streamlink `resolve_url` (pattern match). yt-dlp `ie.suitable` (pattern match). **No network** | n/a |
| DirectResolver | Always “able”; `is_http_live_stream` GETs the URL (`resolver_base.py:94-137`) | Yes, fallback |
| Live URL refresh | Proxy `resolve_url` again (`server.py:353-369`) | Implied by the still-playing stream |
| SponsorBlock enabled | `sponsor.ajay.app` via yt-dlp `SponsorBlockPP`, hash prefix of the video ID (`sponsorblock.py:82-118`). Default **off** (`settings.py:206`) | Opt-in, then automatic on every YouTube play |
| List window, thumbnails on | Thumbnail HTTP, Streamlink session (`thumbnails.py:44-60, 91-109`). `playlist/list_thumbnails` default **True** | List opened; each thumb is extra |
| `playlist/list_get_info` | yt-dlp metadata; default **False** (`settings.py:138`) | Off until asked |
| Settings → Test | YouTube home + test video, or robots.txt | Yes |
| Startup / idle / local file | No resolver, no proxy, no checkup | — |

No update check, telemetry, crash upload, or GitHub poll was found in app code. Crash dialog (`dialogs/exception.py`) shows a traceback (local paths) and a link; Copy is manual. yt-dlp `remote_components` is not enabled; EJS is not fetched from GitHub/npm unless the owner passes that.

**Proposed fix:** Default thumbnails off, or fetch only rows on screen after the owner switches to thumbnail view (already near-viewport, still automatic). Keep SponsorBlock opt-in; document the third-party host. After Streamlink is parked, `stream_detect` / thumbnails / `fetch_capped` must not import it.

---

## F9. Headers and identity on the wire (rule 4)

**Severity:** Low–Medium  
**Where:** `utils/network.py:39-42` `DEFAULT_USER_AGENT` (Chrome/150 on Windows NT 10.0), `:319-322` `vlc_user_agent`; `vlc_player/instance.py:78, 198` instance name `"Mozilla"` + that UA; `player_base.py:135-137` only UA and Referer forwarded to VLC. yt-dlp format `http_headers` go on the proxy session (`resolver_yt_dlp.py:379-382`). Channel-list UA/Referer from `#EXTVLCOPT` / `|User-Agent=` (`list_files.py:544-596`).  
**Confirmed:** No local path, username, or hostname is added by GridPlayer to request headers. Streamlink’s session may still send its own default header set (including locale-derived Accept-Language) when `network/user_agent` is empty. Proxy `do_GET` logs path + headers at DEBUG (`server.py:530`), and for simple streams the path contains the upstream URL (tokens included). ERROR logs full URLs (`url_resolve.py:146, 164`; `media_import.py:277, 301`; `playlist.py:373`). DEBUG `log_environment` dumps `os.environ` (`utils/log.py:24-47`). Default log level is WARNING (`settings.py:187`).  
**Proposed fix:** When not impersonating, send only UA + Referer the site already set on the format. Do not add Accept-Language from the OS locale. Never log URLs at ERROR; log host + status. Strip query from logged URLs. Keep DEBUG env dump behind an explicit “include environment in log” switch. Proxy goes away with F1.

---

## F10. libVLC / FFmpeg versions and modules

**Severity:** High for Flatpak still on 3.0.23; Medium for demux surface; Info for Windows/macOS 3.0.24  
**Where:** Windows/macOS bundle **VLC 3.0.24** (`scripts/pyinstaller/build_win.sh:14`, `build_mac.sh:99-101`). Flatpak still **VLC 3.0.23** + **FFmpeg 4.4.8** (`scripts/flatpak/libvlc/libvlc.yml:73, 236-254`). Vendored bindings `__libvlc_version__ = "3.0.21"` (`vlc_player/vlc.py:55-58`) are the API stub, not the DLL. Daily `uv run gridplayer` uses **system VLC** (`utils/libvlc.py:26-27, 61-74`) if there is no embed.  
**Confirmed (VideoLAN-SB-VLC-3024, Sep 2026):** 3.0.24 fixes 50+ issues in VLC and 74+ in bundled libs, including CVE-2026-56711, CVE-2026-73324, TagLib/picture/WiDi/ARIB/VDR heap overflows, skins2 path traversal, SAT>IP memory disclosure. FFmpeg in that build is **8.1.2** (up from 4.4). RealRTSP disabled in packaged VLC.  
**Modules copied on Windows** (`build_win.sh:61-89`): whole `access`, `codec`, `demux`, `misc`, `packetizer`, `stream_filter`, `audio_*`, `video_output`, `d3d9/11`, plus transform/blend/scale and `text_renderer`. Not copied: `services_discovery` (UPnP/SAP), `control` (http/telnet), `lua`, `stream_out`, GUI. Instance flags: `--no-lua --no-interact --no-keyboard-events --no-mouse-events` (`instance.py:131-151`).  
**Proposed fix:** Pin **3.0.24** (or newer) on every channel, including Flatpak. `uv run` should warn if system libVLC &lt; 3.0.24. Do not copy `misc` plugins that phone home (addons repository, audioscrobbler, fingerprinter) if they are in that folder. Keep `--no-lua`. Do not enable SRT listener / HTTP intf. No ffmpeg CLI in the player; tests use ffmpeg on PATH only (`tests/real_app/media.py`). Do not hand-audit ffmpeg.

---

## F11. Playlist / list / drop parsers

**Severity:** Medium  
**Where / confirmed:**

| Parser | Path | Notes |
|---|---|---|
| JSON `.gpls` | `models/playlist.py:207-217, 330-344` | Pydantic. No pickle/eval. **`Path.read_text` has no size cap** (lists are capped at `player/list_max_mb` default 512 MiB; playlists are not). |
| Legacy `#GRIDPLAYER` | `playlist.py:379-421` | `#P:` JSON via `model_validate_json`. Same unbounded read. |
| URI in playlist | `models/video_uri.py:17-19` | Any string with `://` is kept. **No scheme allowlist** (m3u parser has `URL_ALLOWED_SCHEMES` at `list_files.py:416-423`). `file:`, `smb:`, `ftp:`, `vlc:` can reach VLC access plugins. |
| M3U/PLS | `list_files.py:103-119, 502-596` | Size cap. HLS `#EXT-X-` rejected as “not a list”. Headers only UA/Referer. |
| XSPF | `list_files.py:352-356` | `xml.etree.ElementTree.fromstring`. Python 3.10+ does not expand external entities (no classic XXE). Billion-laughs DoS still possible inside the size cap. |
| Drop / CLI / pipe | `utils/misc.py:40-41` `is_url` = `^[a-z]+://`; `add_videos.py` uses `URL_ALLOWED_SCHEMES` in the add-URL dialog, not necessarily on pipe argv. |
| Cell drag MIME | `utils/files.py:69-79` | `VideoBlockMime.model_validate_json`. |

Relative paths use `os.path.normpath` (`video_uri.py:23-25`); `..` can leave the playlist directory. That is normal playlist behaviour; do not treat as a vuln by itself.

**Proposed fix:** Cap `.gpls` reads (e.g. 32 MiB). Apply `URL_ALLOWED_SCHEMES` in `parse_uri` / `Video.uri`. Keep pydantic. Do not add `defusedxml` unless XSPF from the network becomes common.

---

## F12. Subprocess / shell

**Severity:** Low (no `shell=True` with untrusted text in the app)  
**Where:**

- `player/managers/macos_fileopen.py:32-39` — `open -n … --args <FileOpen path>`. No shell.
- `utils/show_in_folder.py` — `QProcess.startDetached("open"|"xdg-open")`, `os.startfile`, DBus `ShowItems`. Paths only.
- `dialogs/settings.py:851` — `subprocess.call(["xdg-open", folder])` for the data dir.
- `utils/js_runtime.py` — yt-dlp execs Deno/Node/Bun/qjs from PATH, data dir, or `streaming/js_runtime_path`. **Node is not sandboxed** (full FS/network if yt-dlp runs player JS there). Deno is restricted.
- yt-dlp itself, on YouTube resolve, is the only routine subprocess of untrusted JS.

`CommandLoop` (`multiprocess/command_loop.py:41-54`) pickles commands to VLC child processes and `getattr(self, command_name)`. That pipe is parent–child only, not the file-open pipe.

**Proposed fix:** Prefer Deno; do not run Node for YouTube JS unless the owner sets it. Do not pass user strings to `shell=True`. Leave FileOpen/show-in-folder as argv lists.

---

## F13. Privacy trail on disk (outside media folders)

Default data dir: `%APPDATA%\vzhd1701\GridPlayer-Alabaster` (`version.py:24`, `utils/app_dir.py:40-56`). Cache: `%LOCALAPPDATA%\vzhd1701\GridPlayer-Alabaster\cache` (`app_dir.py:59-73`). Portable: `portable_data/` next to the exe. Override: `GP_USER_DATA_DIR`.

| File | Reveals | Default | Proposed |
|---|---|---|---|
| `settings.ini` | Recent videos/playlists (full URLs/paths), `last_playlist`, `network/proxy_url` (may include `user:password`), browser name/profile, keymap, window habits | Written always | Off switch for recent (`player/recent_list_enabled`, already exists, default **on**). Redact proxy userinfo. Do not store cookie values (F3). |
| `gridplayer.log` (+ `.1` `.2` if rotated) | ERROR: full URLs/tokens (`url_resolve.py:146`). DEBUG: env, argv, proxy paths. Default level WARNING, VLC logs disabled | On | Never log query strings. Optional “no file log”. |
| `cookies.txt` | Netscape logins | If imported / updated | **Delete with F3** |
| `media_shapes.json` | Absolute paths + size/mtime + portrait flag (`utils/media_shape.py:18-47`) | On when aspect filter probes | Cap, or keep in memory, or off with the feature |
| `screenshots/` | Frames + titles in names (`%F_%P`, `utils/screenshots.py:46, settings.py:99-102`) | On capture | Already a dir setting; add “don’t use title in filename” |
| `cache/thumbnails/` | Image bytes; key is SHA1 of URL (`cache.py:157-160`) | Disk, 1024 MiB (`settings.py:105-106`) | Memory-only or off; already has `cache/mode` |
| `cache/lists/` | Full channel lists, titles, URLs, zlib JSON (`list_cache.py:18-48`) | Same cache | Off / shorter TTL; contains IPTV URLs |
| Crash dialog clipboard | Traceback with local paths | Manual copy | Keep; do not auto-upload (already true) |
| Windows SMTC / Linux MPRIS / macOS Now Playing | Title of what is playing to other session apps (`utils/media_session.py`) | On when a session exists | Off switch |

`player/reopen_last_playlist` stores the last `.gpls` path (`settings.py:87, 241-242`).

No cookies in the log by design (`cookies.py:7-9`).

---

## F14. Extra findings (not in the original list)

**F14a. Thumbnails default on** — `playlist/list_thumbnails: True`. Opening a YouTube/channel list fetches pictures without a second click. Rule 2 names thumbnail fetches. **Medium.** Default off.

**F14b. JS runtime Node** — YouTube player JS under Node has host FS/network. **Medium.** Deno only unless the owner points at Node.

**F14c. `cookiesfrombrowser` reads the whole browser profile into yt-dlp’s memory**, not one site. Request-time, not stored. Crash dumps could contain it. **Low.** Document; keep in memory; do not write.

**F14d. UDP/RTP/SRT** — `URL_ALLOWED_SCHEMES` includes `udp`, `rtp`, `rtsp`, `rtmp`, `mms`, `mmsh`. Playing those *will* bind. SRT listener mode is new in VLC 3.0.24. **Info.** Allowed only when the owner opens such a URL; never at idle.

**F14e. Process-tree VLC children** — hardware driver spawns VLC processes. A listen-socket test must include children, not only the UI process.

**F14f. Overlay live timestamp** — upstream #309 (`OSError` in `gmtime`) is closed in `52c706d`. This fork clamps negatives (`time_txt.py:11`, `video_overlay.py:401`) but still calls `time.gmtime` (`time_txt.py:108-114`). Huge live positions can still throw on Windows. **Low.** Clamp to `0 … 359999` (or drop `gmtime`).

**F14g. No app telemetry** — confirmed. Keep it that way when adding plugins.

---

## Streamlink → plugin later; yt-dlp as the only built-in resolver

Today: `streaming/resolver_priority` = **STREAMLINK** (`settings.py:197`). YouTube is forced to yt-dlp. The proxy, live HLS, thumbnails, checkups, `http_in_playlists.py`, and `stream_detect.py` import Streamlink.

**Default-path change (fix phase, once approved):**

1. Default resolver = yt-dlp. Remove Streamlink from `_resolver_map` unless a plugin is loaded.
2. Stop importing Streamlink from `network.py`, `thumbnails.py`, `stream_detect.py`, `http_in_playlists.py`, `ytdlp_checkup.py`, `network_checkup.py`, `resolver_base.py`.
3. Kill the stream proxy (F1).
4. Keep Streamlink **in the tree** as the first plugin candidate; do not delete `resolver_streamlink.py` or the HLS rewrite knowledge in `stream_proxy/wrappers.py` (`HLSProxy`, fragment-by-position, key rewrite, live vs VOD, muxed audio). Those are the plugin’s job later.

**What Streamlink does today that yt-dlp+VLC must replace:**

| Behaviour | Streamlink / proxy | yt-dlp-only without listener |
|---|---|---|
| Per-segment headers & cookies | Proxy rewrites playlist to localhost; session cookies on every GET | Media callbacks, or VLC-native HLS if only UA/Referer needed |
| AES-128 keys in HLS | Proxy fetches key URI with session | Same: callbacks, or VLC if the key URL is public |
| Muxed HLS (video + audio renditions) | `MuxedHLSStream` → master playlist via proxy (`wrappers.py` `build_master_playlist`) | yt-dlp separate formats + VLC input-slave, or callbacks mux |
| Live edge / sliding window | Streamlink HLS client; proxy still in the way (F5) | **Give VLC the live m3u8** (`"direct"`). Do not snapshot the window as VOD |
| Twitch | Streamlink plugin (ad filtering, usher, LL-HLS) | yt-dlp Twitch extractor; **ads may play**; LL-HLS may be worse |
| Kick | Streamlink plugin (may still 403) | yt-dlp extractor + **curl_cffi impersonate on every segment**; VLC cannot fetch (F6) |
| RAI / DVR-style live (#320) | Mis-detect as VOD → hours behind | Live m3u8 to VLC; fix `is_live` |
| Generic m3u8 (#239) | Not the same as VLC opening the URL | Direct m3u8 to VLC is the VLC-like path |
| `http://` segments in `https://` playlists | Monkeypatch `M3U8Parser.uri` (`http_in_playlists.py`) | Replicate in the yt-dlp/VLC path if still required; default is already allow |
| `streamlink.webbrowser` (#160) | **Not wired.** No Chromium launched | Keep it out of the default app. Plugin-only, opt-in, never at startup |

**Do not enable Streamlink webbrowser in core.** It launches a real browser, which is extra network and a fingerprint the owner did not ask for on every stream.

---

## Upstream bugs, yt-dlp-only (retest in fix phase)

**#320 live broadcasts** (open) — RAI live (`raiplay.it/dirette/rai1`) starts hours early. Code cause: treating a live window as VOD and playing from the first listed segment (`HLSProxy._is_served_by_position`, `is_live` false). **Fix: VLC follows the live manifest; do not rewrite a snapshot.** Retest that URL with yt-dlp only.

**#239 m3u8 links** (open) — “don’t open like they open in VLC.” Direct m3u8 + libVLC HLS is the VLC-like path. Proxy rewrite is the divergence. Retest the reporter’s class of IPTV m3u8 after F1.

**#309 live HLS overlay crash** (closed upstream `52c706d`) — `get_time_txt` → `gmtime` `OSError` on invalid live time. This fork clamps negatives; retest a live HLS grid for overlay crashes; tighten `gmtime` (F14f).

**#160 streamlink.webbrowser** (open enhancement) — not implemented; **do not implement in core.** Candidate for a Streamlink plugin later.

Live playback was **not** executed in this phase.

---

## Plugin interface (later, no code)

Keep a resolver interface close to `ResolverBase` (`url_resolve/resolver_base.py`): `is_able_to_handle`, `resolve()` → `ResolvedVideo` / `ResolvedList`, optional `headers`, no listener.

- **Streamlink plugin:** wrap `StreamlinkResolver` + HLS handling from `stream_proxy/wrappers.py`. Opt-in. Network only when that plugin is chosen for a URL.
- **SubtitleCat:** network only when the owner asks for subtitles. Request-time cookie from the owner’s browser, memory only. Anything persisted stays inside the plugin, never in core `cookies.txt` / settings. Chrome UA + TLS fingerprint is the plugin’s problem, not core’s.
- **Local media analyzer:** ffprobe/MediaInfo, no network. Yellow/red flags for this Intel Iris Plus + Quick Sync box. Opt-in.

Core must not grow a shared cookie jar “for plugins.”

---

## Verification required in the fix phase (do not implement now)

1. **No listening TCP/UDP** — start the app offscreen, play a **local** file, walk the **process tree** (UI + VLC children) with `psutil.Process().net_connections()` and/or Windows `GetExtendedTcpTable` / `GetExtendedUdpTable`. Fail on `LISTEN` / `BOUND` for TCP or UDP on any address including 127.0.0.1 and `::1`. Then play a **stream** (yt-dlp path) and assert still no listener.
2. **No outbound on startup + local playback** — fail on any `ESTABLISHED` / `SYN_SENT` that is not loopback, and on DNS if you can see it. Allow outbound only after a stream URL is opened, and only to that stream’s hosts (plus opt-in SponsorBlock).
3. **No `cookies.txt`** after a resolve with `--cookies-from-browser`.
4. **Kick (optional, 64-bit):** play a Kick URL; must not 403-skip all formats; must not open a port.

---

## Suggested fix order (for approval)

1. F3 stored cookies out; keep from-browser.  
2. F1/F5/F6 proxy out; yt-dlp + libVLC options + media callbacks; Kick via curl_cffi.  
3. Default resolver yt-dlp; Streamlink off the import path; leave sources for a plugin.  
4. F2 pipe: JSON, DACL, `PIPE_REJECT_REMOTE_CLIENTS`, no pickle.  
5. F4 VLC options deny-list; F10 pin VLC 3.0.24 everywhere.  
6. F11 URI allowlist + gpls size cap; F9 log redaction; F13/F14a recent/thumbs defaults.  
7. Tests in the verification section.  
8. Retest #320, #239, #309 with yt-dlp only.

Waiting on owner approval before any code change.
