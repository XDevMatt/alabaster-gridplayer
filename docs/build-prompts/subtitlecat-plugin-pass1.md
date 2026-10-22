# Build prompt: SubtitleCat plugin, pass 1 (GridPlayer Alabaster)

Owner: XDevMatt. Approved to build. Read `AGENTS.md`, `HANDOFF.md`, `docs/audit/security-privacy-findings.md` and `docs/audit/fix-pass-1.md` first. Every hard requirement there still applies: no listening sockets, no network unless the owner asks, no stored cookies, minimum metadata.

## Working rules
- Work in this folder on `master`. Revert point: tag `pre-subtitlecat-2026-10-22`. Do not push or touch remotes, and make no other copies.
- Small commits with `git -c user.name=XDevMatt -c user.email=341465779+XDevMatt@users.noreply.github.com commit`. Leave the uncommitted ruff-format edits to unrelated files alone, and do not commit them.
- Follow AGENTS.md: edit `.ui` sources and run `just generate-ui` (never edit `*_ui.py`), use literal `translate("Context", "Text")`, put new block behavior in a `VideoBlockPart`, don't touch vendored `vlc.py` or the translations.

## Owner stance: the app is a signpost, not a provider
- Alabaster bundles no SubtitleCat account, key, cookie or content, and never hosts, caches for others or redistributes subtitles.
- Each user signs up and signs in at subtitlecat.com in their own browser. The plugin settings show "Sign up" and "Sign in" buttons that only open `https://www.subtitlecat.com/register.php` and `/login.php` in the default browser when clicked.
- Every SubtitleCat request (search, download, translate) runs on the user's own session, so it counts against their own account limits. At request time, read only the `subtitlecat.com` cookies from the browser chosen in the existing `cookies/from_browser` and `cookies/browser_profile` settings, using yt-dlp's browser-cookie reader. Keep them in memory for that request only. Never write them to disk, settings or logs.
- If no session is found, make no request. Show: "Sign in to SubtitleCat in <browser> first", with the Sign in button.

## What SubtitleCat publishes (checked 10-22-2026)
- No terms of service. robots.txt is `Allow: /` with a sitemap. The API is enterprise-only, through partnership.
- Free accounts get limited translations, lines per hour and uploads. Existing translations are unlimited. VIP costs $6/month.
- Search is GET `https://www.subtitlecat.com/index.php?search=<terms>`. The results table links to `subs/<n>/<name>.html` and shows size, downloads and languages.
- A subtitle page has `a#download_<lang>` with `href="/subs/<n>/<name>-<lang>.srt"` for existing translations, and `translate_from_server_folder('<lang>', '<file>', '/subs/<n>/')` buttons for languages not yet translated.
- Verify all of this live once while building, and adapt if it changed.

## Build
1. **A minimal plugin layer.** Plugins are opt-in, off by default, and enabled in Settings. They are not imported until enabled. They're shaped so Streamlink can become a plugin later (do not move Streamlink in this pass). A plugin gets no shared cookie jar.
2. **The SubtitleCat plugin.** Add a cell menu action, "Find subtitles on SubtitleCat…". It opens a dialog prefilled with search terms cleaned from the file name, which the user can edit. It lists the results, then a result's available languages, with the owner's preferred language first.
   - Download saves the `.srt` beside the video; if that folder isn't writable, it goes to the Alabaster data folder's `subtitles\`. It loads the file into the cell through the existing subtitle-file path.
   - Filenames: no apostrophes. Drop them and join the letters, e.g. `Britains`.
3. **Translate**, off by default with its own toggle. It requests a new translation with the user's session. It shows SubtitleCat's own limit or VIP messages as-is, and never retries, rotates or works around a limit.
4. **Polite traffic.** Requests happen only on a user click. One request at a time, at least 1 s apart, no bulk crawl or prefetch, and a timeout with a clear error. Use the app's existing network settings and User-Agent from `gridplayer/utils/network.py`, and send no Referer beyond subtitlecat.com.

## Tests
- Parsers run against saved HTML fixtures (use a non-adult search for them). Tests make no live network calls.
- No request goes out without a session, a user action, or with the plugin disabled.
- Cookies never reach disk, settings or logs.
- The plugin opens no listening socket.
- Filename sanitizing covers apostrophes and path characters.
- Optional: a live smoke test behind an env flag.

## Deliverable
`docs/plugins/subtitlecat-pass-1.md`: commits, what works, how it was verified, the live check of the site structure, and open decisions. Update the plugin note in AGENTS.md. Then stop.
