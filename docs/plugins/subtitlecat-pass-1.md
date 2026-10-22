# SubtitleCat plugin, pass 1

Date: 2026-10-22. Owner: XDevMatt. Branch: `master`. Revert point: tag
`pre-subtitlecat-2026-10-22` (`7ae9dd3`). These commits are local. Nothing
was pushed.

Alabaster bundles no SubtitleCat account, key, cookie, or subtitle file.
It does not host subtitles or keep a copy for anyone else. Each request
runs on the user's own subtitlecat.com session.

## Commits

| Commit | Subject |
| --- | --- |
| `255fd04` | Plugins: keep SubtitleCat unloaded until its setting is on. |
| `5490757` | SubtitleCat: parse result pages and clean subtitle file names. |
| `e8e3048` | SubtitleCat: one signed-in request at a time, then drop the cookies. |
| `4994156` | SubtitleCat: add the cell action that searches and downloads. |

This file, the Plugins section in `AGENTS.md`, and the NOTICE change-list
line are the documentation commit. Unrelated ruff-format edits that were
already in the tree were left unstaged.

## What works

Plugins are opt-in. `plugins/subtitlecat` and `plugins/subtitlecat_translate`
default to off. The catalog is data. `load()` imports
`gridplayer.plugins.subtitlecat` only when the setting is on. Importing
the catalog, or the cell part, does not import the plugin, Streamlink, or
yt-dlp. Streamlink was not moved. A plugin has no shared cookie jar.

Settings has a Plugins heading and a SubtitleCat page. Enable SubtitleCat
and Request translations are separate checkboxes. Request translations
stays available when the plugin checkbox is off, because a disabled
widget is skipped on save. Sign up opens
`https://www.subtitlecat.com/register.php`. Sign in opens
`https://www.subtitlecat.com/login.php`. Any other URL is ignored. The
buttons are not settings keys.

With the plugin on, a cell that has a video shows Subtitles → Find
subtitles on SubtitleCat…. The dialog opens with search words cleaned
from the file name. Britain's becomes Britains. Opening the dialog does
not search.

Search is GET `https://www.subtitlecat.com/index.php?search=<terms>`.
The list keeps `https://www.subtitlecat.com/subs/<n>/<name>.html` and
skips Load More and off-site links. Choosing a result lists languages.
The cell's subtitle languages come first, then the player language's
primary tag. `en` matches `en` and `en-GB`. `zh-TW` matches only itself.

Download writes the `.srt` beside a local video when that folder accepts
a probe file. Otherwise it writes to the Alabaster data folder's
`subtitles` directory. The saved file is loaded with
`subtitles.add_external`. Apostrophes are dropped. `< > : " | ? *`,
slashes, and control characters are removed. The last path segment is
taken before percent-decoding, so `%2F` cannot leave the folder
(`a%2F..%2Fb.srt` becomes `a..b.srt`). An existing file becomes
`name-2.srt`.

Translate stays hidden until both settings are on. One click is one POST
to `https://www.subtitlecat.com/request_shared_translation.php` with
`to_language`, `filename`, and `folder`. The subtitle text is not sent.
The reply is shown as SubtitleCat sent it, including a limit or VIP
sentence. There is no retry. A JSON body that names a subtitlecat.com
`.srt` offers Download as a second click. A body that is itself a
subtitle is held in memory until that click.

Requests happen on a button click. One runs at a time, with at least one
second between them. The plugin setting is checked before cookies and
before HTTP. An empty search, a disabled plugin, a disabled translate
toggle, or a missing session makes no request. No browser on the Cookies
page shows "Choose a browser on the Cookies page, then sign in to
SubtitleCat there first". A browser with no login cookie shows "Sign in
to SubtitleCat in &lt;browser&gt; first", and the dialog's Sign in button
is there.

Cookies come from yt-dlp's `extract_cookies_from_browser`, using
`cookies/from_browser` and `cookies/browser_profile`. Only
`subtitlecat.com` and `*.subtitlecat.com` are copied into a plain
`CookieJar`. A login-like name is required before anything is sent.
`cf_clearance` alone is not a session. Once a session is found, the
request sends the copied subtitlecat.com cookies, then both jars are
cleared. The quiet logger drops yt-dlp's messages. URLs, queries, and
cookie values are not logged. User-facing network errors are fixed
sentences.

The client uses the app proxy mode, User-Agent (`vlc_user_agent`), TLS
verify flag, and IPv4 source address from `gridplayer/utils/network.py`.
Timeout is `network/timeout`, or 20 seconds when that value is 0. No
`Accept-Language` header is sent. Referer is sent only for
`subtitlecat.com` and `www.subtitlecat.com`. An off-site URL or redirect
is refused before a request carries the cookie. HTML answers are capped
at 2 MiB and downloads at 8 MiB. "No proxy" passes an empty
`ProxyHandler` so urllib does not add the machine proxy. On Python 3.12
that empty handler is then dropped, and the opener has no proxy address.

## How it was verified

Parsers, names, the client, the save path, the dialog, the part, the
settings page, and the menu were tested with pytest. The tests use saved
HTML and a fake transport. They make no live HTTP call. The optional
smoke test stays skipped unless `GRIDPLAYER_SUBTITLECAT_LIVE=1`. That
flag was not set, and the live test was not run.

Command:

```text
uv run pytest tests/test_plugins.py tests/test_subtitlecat_names.py
tests/test_subtitlecat_parse.py tests/test_subtitlecat_save.py
tests/test_subtitlecat_client.py tests/test_subtitlecat_dialog.py
tests/test_subtitlecat_part.py tests/test_subtitlecat_settings.py
tests/test_settings_sections.py tests/test_dotted_commands.py
tests/test_menu_subtitle_delay.py tests/test_settings_cookies.py
tests/test_menu_subtitle_track.py -q --tb=line -p no:cacheprovider
```

Result on 2026-10-22: 388 passed, 2 skipped, 2 failed, in 24.58s.

The two skips are `psutil is not installed` and the live smoke test.
`psutil` is not a project dependency, so the listening-socket pytest did
not run. A separate check started the project interpreter, imported
`SubtitleCatClient`, constructed it with the plugin off, and queried that
process. `Get-NetTCPConnection` reported no TCP connections and
`Get-NetUDPEndpoint` reported no UDP endpoints. The plugin package does
not call `bind` or `listen`.

The two failures are pre-existing and outside this work:
`tests/test_dotted_commands.py::test_manual_seek_reaches_a_part_and_syncs_the_others`
and `test_manual_seek_of_a_part_that_went_nowhere_syncs_nothing`. Both
raise `TypeError: isdeleted() argument 1 must be sip.simplewrapper, not Mock`
in `gridplayer/widgets/video_block_guards.py`. The new
`subtitlecat.find` command is in the same file's passing tests.

`uv run ruff format` and `uv run ruff check` were run on the plugin,
dialog, part, settings, menu, and new tests. They passed.

The settings page was generated from `resources/ui/settings_dialog.ui`
with `uv run pyuic5` on that file only, then ruff format and
`ruff check --fix` on `gridplayer/dialogs/settings_dialog_ui.py`. The
generated diff is the new page (88 insertions, 2 deletions).
`just generate-ui` was not run. Its recipe converts every file in
`resources/ui` and rewrites every `dialogs/*_ui.py`.

The real player was not launched. Dialog tests drive the widgets
offscreen and replace `OffThread.run`, so no network thread starts.

## Live check of the site structure

Checked once on 2026-10-22 while building. Not fetched again during the
commit pass.

`https://www.subtitlecat.com/robots.txt` is `Allow: /` and names a
sitemap. No terms of service were found. The public pages used below are
the search form and the subtitle HTML pages. The enterprise API was not
called.

Search `Sintel` is GET `https://www.subtitlecat.com/index.php?search=Sintel`.
The results table links to `subs/<n>/<name>.html` and shows size,
downloads, and a language count. Rows seen that day included
`subs/752/...rum.html` (Romanian, 2 KB, 1 download, 1 language),
`subs/751/...AAC....html` (Romanian, 2 KB, 10 downloads, 10 languages),
`subs/751/Sintel (2010).eng.html` (English, 2 KB, 19/19), and
`subs/1434/classicalhd-sintel.2010.en-1080p.html` (English, 36 KB, 1/1).
Load More points at `index.php?search=Sintel&show=1000`. The plugin does
not follow it.

A subtitle page has `div.sub-single`, a flag image, and
`a#download_<lang>` whose `href` is `/subs/<n>/<name>-<lang>.srt`. The
`.srt` number can differ from the HTML page's number. Language ids
include `zh-TW` and `es-419`. A language that has no file yet is a button
calling `translate_from_server_folder('<lang>', '<file>', '/subs/<n>/')`.
`login.php` and `register.php` both exist. The VIP price shown on the
site was "Just only $6 per month", linking toward `register.php`.

The page's own `translate.js` batches text to Google in the browser and
then uploads the result. The paid path posts to
`request_shared_translation.php`. That script was not vendored. The
fixtures under `tests/fixtures/subtitlecat/` are structural excerpts of
the Sintel pages. They contain no subtitle cues.

## Open decisions

1. Translate is one POST of `to_language`, `filename`, and `folder`. It
   does not run the Google batch loop, does not send subtitle text, and
   does not call `upload_subtitles`, `upload_private_subtitles`,
   `get_shared_translation`, or `visitor_log`. If
   `request_shared_translation.php` answers with a limit or with HTML
   and no file, that text is what the user sees. This was not tried
   against the live site.

2. A cookie named `PHPSESSID`, or any non-analytics name containing
   `sess`, `auth`, `login`, `remember`, `token`, or `user`, counts as a
   session. An anonymous `PHPSESSID` can therefore allow a request. The
   site's reply is shown. A login cookie whose name matches none of
   those pieces, such as `sc_id`, is missed, and the user is asked to
   sign in.

3. Load More (`show=1000`) is not requested. The first results page is
   the whole search.

4. When `network/timeout` is 0, the wait is 20 seconds. A timeout is
   reported as "SubtitleCat did not answer in time."

5. The plugin never calls `CookieJar.save` and never writes cookies into
   settings, the log, or the Alabaster data folder. yt-dlp's reader
   copies the browser's cookie database into a `tempfile.TemporaryDirectory`
   (prefix `yt_dlp`) so it can read a locked SQLite file, and that
   directory ends with the `with` block. That copy belongs to yt-dlp's
   reader, which this pass was told to use.

6. "No proxy" is an empty `ProxyHandler`. urllib then skips the
   environment proxy. Python 3.12 does not keep that empty handler on
   the opener, because it installs no protocol method. The result is a
   direct connection, with no proxy address stored on the opener.
