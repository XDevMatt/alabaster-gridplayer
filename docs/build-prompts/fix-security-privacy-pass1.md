# Build prompt: security and privacy fix pass 1 (GridPlayer Alabaster)

Owner: XDevMatt. The owner APPROVED the fixes from `docs/audit/security-privacy-findings.md`. Read that report and `docs/build-prompts/audit-security-privacy.md` first; their hard requirements still apply. You are the expert: fix what the report found, and fix anything else you hit that breaks those rules.

## Working rules
- Work directly in this folder on branch `master`. The revert point is tag `pre-fix-pass-2026-10-22`. Do not push, do not touch remotes, do not create other copies or worktrees.
- Commit in small, separate commits, one fix per commit, with `git -c user.name=XDevMatt -c user.email=341465779+XDevMatt@users.noreply.github.com commit`. Never use any other identity or real name.
- Do not delete anything outside this repo. If the user's settings folder holds a stored cookie jar or cookie file, stop using it, but leave the file in place and list its path in the report.
- Run the existing tests plus the new ones after each fix. Leave the app runnable with `.venv\Scripts\pythonw.exe -m gridplayer`.

## Fix order
1. **File-open pipe** (`gridplayer/utils/single_instance.py`). No pickle: send a plain, length-limited UTF-8 or JSON list of paths, and validate it before use. Reject remote clients and restrict the pipe to the current user (security descriptor). Use an authkey or equivalent if `multiprocessing.connection` stays.
2. **Stream proxy.** Remove the `ThreadingHTTPServer` listener from the default path. yt-dlp is the only built-in resolver: hand VLC the direct media URL plus required headers as libVLC media options. For streams that need impersonation (Kick), feed VLC through `libvlc_media_new_callbacks` from yt-dlp with curl_cffi, with no listener. If one stream type can't work without a listener yet, disable it with a clear message rather than keep the listener, and list it in the report. Fix the live-window-as-VOD bug (#320/#239) and the `gmtime` overflow (#309) on the way.
3. **Cookies.** No stored jar: default off, remove `cookies/allow_update` write-back, the stored jar, and the import/export paths. Keep only request-time `--cookies-from-browser`, in memory.
4. **`misc/vlc_options`.** Block options that open listeners (http, sout, rc, telnet and similar interfaces) or re-enable Lua; always force `--no-lua` last.
5. **yt-dlp provenance.** Always use the bundled `yt_dlp` Python module from this app's environment, never a `yt-dlp` executable found on PATH. Add an opt-in setting to use an external yt-dlp binary at a chosen path, off by default, with a strong warning dialog before enabling that explains that a binary on PATH can be impersonated. Update the bundled module: `.venv\Scripts\python.exe -m pip install -U yt-dlp` and record the old and new versions.
6. **JavaScript runtime pinning** (`gridplayer/utils/js_runtime.py`). By default pass yt-dlp only an engine inside the app folder (for example `vendor\deno\deno.exe`). You may download the official Deno Windows x64 release from github.com/denoland/deno releases into `vendor\deno`, verify its published SHA-256, and record version and hash; do not commit the binary (gitignore it) and document how to fetch it. Engines found on PATH become an opt-in with the same strong warning as item 5.
7. **Streamlink** stays in the tree as a future plugin, off the default import path, as the report recommends.

## Tests required
- The app starts offscreen, plays a local file, and the process never opens a listening TCP or UDP socket.
- No outbound connection during startup and local playback.
- The pipe rejects a pickled payload and malformed input.
- vlc_options filtering, and yt-dlp/JS runtime resolution ignores PATH unless opted in.

## Deliverable
`docs/audit/fix-pass-1.md`: per fix, the commit hash, what changed, how it was verified, and anything left undone or needing an owner decision. Then stop.
