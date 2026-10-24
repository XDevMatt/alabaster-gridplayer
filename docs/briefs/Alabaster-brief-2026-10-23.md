# Alabaster brief - 2026-10-23

Owner: XDevMatt. Repo: `WebAutomation\gridplayer_fork`, branch `master`. All commits local, nothing pushed.

## 1. SubtitleCat plugin, pass 1 (10-22)

What it does
- Opt-in plugin, off by default. Not loaded until its setting is on.
- Cell menu: Subtitles > Find subtitles on SubtitleCat. Search words come from the file name.
- Pick a result, pick a language, download the .srt next to the video (or the Alabaster data folder `subtitles` dir). It loads into the cell.
- Optional "Request translations" button (second setting). One click = one request. No retry.
- Settings has a Plugins page with Sign up / Sign in buttons (open subtitlecat.com only).

Zero-trust behavior
- Ships no SubtitleCat account, key, cookie or subtitle file. Hosts nothing.
- Uses your own browser session, read at request time; only subtitlecat.com cookies, dropped after the request.
- No request on: empty search, plugin off, translate off, or no session.
- One request at a time, at least 1 second apart. Only on a button click.
- File names cleaned; path tricks like `%2F` cannot escape the folder. Never overwrites (`name-2.srt`).

Tests
- 388 passed, 2 failed (pre-existing seek tests), 2 skipped.

Open calls
- PHPSESSID counts as a session (may be a guest cookie).
- Only the first results page is read.
- Translate not tested live.

Revert
- `git reset --hard pre-subtitlecat-2026-10-22`

## 2. License update - commit bf4160b (10-23)

- Deno (MIT) credited in NOTICE, About and README.
- NOTICE dates run through 10-23.
- Security changes listed in NOTICE.
- Cookie line fixed.
- Note: ffmpeg ships inside VLC.
- SubtitleCat non-affiliation statement.
- Revert: `git reset --hard pre-license-2026-10-23`

## 3. Security fix pass (10-22)

- Revert tag: `pre-fix-pass-2026-10-22`
- XDevMatt open calls:
  - Wire the external yt-dlp setting, or leave it as a placeholder?
  - Bump Deno 2.5.6 to 2.9.8?
  - Remove the dead Streamlink HLS checkbox?

## 4. Found issues

- Installer / PyInstaller spec ships no `vendor\deno` and no license files. An installed build may lose YouTube. The venv runs fine.
- README stale: still mentions the 127.0.0.1 proxy and JS runtime PATH search; curl_cffi attribution missing.
- 3 failing tests in `tests/test_ytdl_js_runtimes.py` - likely expect the old PATH / data-folder lookup.

## 5. Settings changed on 10-22

- File: `%APPDATA%\vzhd1701\GridPlayer-Alabaster\settings.ini`
- `one_instance=True`
- playlist `unsaved_changes=discard`
- Backups: `settings.ini.backup-2026-10-22-1424` and `settings.ini.backup-2026-10-22-1650`

## 6. Windows virtual desktops

- PowerToys Keyboard Manager: set to Disable
  - Win+Ctrl+D
  - Win+Ctrl+Left / Win+Ctrl+Right
  - Win+Ctrl+F4
- Four-finger swipes: already off.