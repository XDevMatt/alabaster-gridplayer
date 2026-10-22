# Fix pass 1 — security and privacy

Owner: XDevMatt. Revert point: tag `pre-fix-pass-2026-10-22`.
No remotes were touched.

Identity on every commit: `XDevMatt <341465779+XDevMatt@users.noreply.github.com>`.

---

## 1. File-open pipe (F2)

**Commit:** `ac25c54e6ef6f8ccabcd3e70fec90213c7f44a24`

**What changed:** `gridplayer/utils/single_instance.py` no longer uses
`multiprocessing.connection` pickle. The pipe speaks 4-byte big-endian
length + UTF-8 JSON (`{"v":1,"files":[...],"pid":N}`). Payloads over 1 MiB,
more than 1024 items, or non-strings are rejected. Pickle protocol bytes
(`0x80…`) are rejected before `json.loads`. Paths must exist as files or
directories; URLs must use `URL_ALLOWED_SCHEMES`.

Windows: `CreateNamedPipeW` with `PIPE_REJECT_REMOTE_CLIENTS`,
`FILE_FLAG_FIRST_PIPE_INSTANCE`, and a DACL for the current user only
(`ConvertStringSecurityDescriptorToSecurityDescriptorW`).
`AllowSetForegroundWindow` is granted to the running instance PID
(`GetNamedPipeServerProcessId`), not `ASFW_ANY`.

Linux: `AF_UNIX` socket `chmod 0o600`, directory `0o700`.

**Verified:** `tests/test_single_instance.py` (JSON roundtrip, pickle
reject, malformed JSON, scheme/path checks, live named-pipe integration
on this Windows box). `tests/test_tray.py` still passes for
`_handle_input_data`.

**Left:** Optional HMAC with a per-install key was not added. Same-user
local processes can still send a valid JSON list of existing files.

---

## 2. Stream proxy removed (F1 / F5 / F6); live HLS; gmtime

**Commit:** `0cc46639ea3b97f51883496199d300a163f5fefe`

**What changed:**

- `StreamProxyManager.cmd_add_stream` returns the media URL and never
  starts `ThreadingHTTPServer`.
- yt-dlp protocols: live and VOD HLS are `"hls"` (VLC follows the
  manifest — this is the #320 / #239 fix). Impersonation and extra
  headers VLC cannot send use protocol `"callback"`.
- `libvlc_media_new_callbacks` + `YtdlpByteSource` pull bytes from the
  bundled `yt_dlp` module (`curl_cffi` when `impersonate` is set). No
  listener.
- DirectResolver always hands `"direct"`.
- `stream_detect.py` uses urllib on the default path (Streamlink session
  still accepted if a plugin passes one).
- Overlay clocks no longer call `time.gmtime` (#309 / F14f).

Streamlink resolver and `stream_proxy/` sources stay in the tree.

**Verified:** `tests/test_resolver_yt_dlp_streams.py`,
`tests/test_ytdlp_byte_source.py` (manager does not start a listener),
`tests/test_stream_detect_hls_live.py`, `tests/test_utils_time_txt.py`
(including `2**31` and `10**12` seconds).

**Not live-tested:** Kick URL playback, RAI live (#320 URL), IPTV m3u8
(#239). Those need a network pass on the owner's machine.

**Stream types that need callbacks (no listener):** Kick / any format
with `impersonate`; silent video + separate audio that is not the same
manifest URL. 32-bit Windows still has no curl-cffi wheel; Kick stays
unsupported there.

**External yt-dlp binary** (item 5) is a setting only; extract still
uses the bundled Python module. Wiring `yt-dlp --dump-json` is listed
under leftovers.

---

## 3. Cookies (F3)

**Commit:** `82967ad20cf0512896d42b7760d40354ecbd0bbd`

**What changed:** Stored jar, import/export, `cookies/enabled`, and
`cookies/allow_update` are gone. `ytdl_cookies()` yields only
`cookiesfrombrowser` from `cookies/from_browser` +
`cookies/browser_profile`, in memory. The leftover file is not read and
not deleted.

**Leftover jar path (leave in place if present):**

`C:\Users\<user>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster\cookies.txt`

On this machine that file was **not present** at fix time. Portable
builds would use `portable_data/cookies.txt` next to the exe. Override:
`GP_USER_DATA_DIR\cookies.txt`.

**Verified:** `tests/test_cookies_applied.py`,
`tests/test_settings_cookies.py`, `tests/test_cookies_store.py`.

---

## 4. `misc/vlc_options` (F4)

**Commit:** `2e496890308edccd1b1317134f3dc5a2770a9723`

**What changed:** `filter_vlc_options` drops http/https/rtsp/telnet/rc
ports, `--extraintf`, `--control`, `--sout*`, `--lua*`, and
`--intf=http|telnet|rc`. `with_no_lua_last` always appends `--no-lua`
after the settings tokens so they cannot re-enable Lua.

**Verified:** `tests/test_vlc_options_filter.py`.

---

## 5–7. yt-dlp provenance, JS runtime pin, Streamlink parked

**Commit:** `ccea668a34cca48a0646f9a64b07399a5f600c6c`

**yt-dlp:** Bundled module `yt_dlp` only. Never `shutil.which("yt-dlp")`.
Setting `streaming/ytdlp_external_path` (empty default) plus a warning
dialog. Playback still uses the module; the path is stored for a later
subprocess extract if the owner wants it.

**Versions:** old **2026.8.19**, new **2026.10.21** (`uv lock --upgrade-package yt-dlp`).
Transitive lock bump: certifi 2026.7.22 → 2026.10.19.

**JS runtime:** Default `ytdl_js_runtimes()` is Deno at
`vendor/deno/deno.exe` (a concrete path, so yt-dlp does not search
PATH). `streaming/js_runtime_allow_path` restores the old search after
the same warning.

**Deno fetched (not committed):** official
`deno-x86_64-pc-windows-msvc.zip` from
https://github.com/denoland/deno/releases/tag/v2.5.6

- version: **v2.5.6**
- SHA-256 of `deno.exe`:
  `3e367a556068d04e02854add2295a68e7f1cfe6e3e1353027907fd3a0f1b8580`

Fetch again: `scripts/fetch_deno_windows.ps1`. Latest stable at audit
time was v2.9.8; owner can bump the script.

**Streamlink:** Removed from `_resolver_map`. Default
`streaming/resolver_priority` is `YT_DLP`. `STREAMLINK` in old settings
falls back to yt-dlp. `resolver_streamlink.py` and `stream_proxy/` remain
for a plugin.

**Verified:** `tests/test_ytdlp_provenance.py` (PATH ignored unless a
chosen file exists), `tests/test_ytdl_js_runtimes.py` (vendor pin,
opt-in restores engines), `tests/test_stealth_sockets.py` (proxy manager
does not bind).

---

## Tests run

After each fix, the new tests plus the touched existing files. Full
`uv run pytest` still shows the pre-existing
`sip.isdeleted() … not Mock` failures on video-block tests and
`test_video_errors::TestVLCSaid::test_since_the_video_began_to_open`
(HANDOFF known). Those are unrelated to this pass.

Stealth requirements that need the **real app + VLC process tree**
(no LISTEN/BOUND, no outbound on local playback) are only covered at
unit level here. Run a `tests/real_app` scenario with `psutil` on the
owner box to close that gap.

App launch command is unchanged:
`.venv\Scripts\pythonw.exe -m gridplayer`

---

## Owner decisions / leftovers

1. **Wire `streaming/ytdlp_external_path` to a subprocess extract**, or
   keep the bundled module only and treat the setting as a future switch.
2. **Bump Deno to v2.9.8** if you want current stable.
3. **Kick live playback** was not played. Callbacks are in; confirm on
   a 64-bit machine with `vendor/deno/deno.exe` present.
4. **HMAC on the file-open pipe** (report optional) was not added.
5. **Thumbnails default-on (F14a)**, gpls size cap (F11), log redaction
   (F9) were in the suggested later order and were not this pass.
6. **`streaming/hls_via_streamlink`** is still in the settings UI; it no
   longer changes protocol.
7. Accidental `ruff format` of unrelated files
   (`playlist.py`, `media_shape.py`, `video_block_navigation.py`, some
   tests) was **not committed**. Working tree may still show them.

Stop.
