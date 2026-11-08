# Subtitles

Everything here is on the right-click menu under **Subtitles**, per cell.

## Turn subtitles on

- **Subtitles > Subtitle Track** picks a track, or a subtitle file you added.
- New cells start with subtitles **Off**. Settings, Defaults, New Videos,
  Subtitles can start them on the file's **Default** track, or a
  **Preferred Language** (languages best first).

## Add a subtitle file

- **Drop it on the cell.** Drag one or more subtitle files (`.srt`, `.ass`,
  `.ssa`, `.vtt`, `.sub` and the other kinds VLC reads) from Explorer onto a
  cell. They're added to that cell, not opened as videos.
- **Detect external subtitle files** (New Videos, Subtitles, off by
  default): subtitle files next to the video with the same name are offered
  in **Subtitle Track**. They're opened only when you pick one.
- Files that aren't UTF-8 use **Text encoding** (New Videos, Subtitles).
  UTF-8 is detected on its own; ASS and SSA files aren't affected.

## Subtitle delay (`H` / `G`)

| Do | This cell | Every cell |
| --- | --- | --- |
| Subtitles later | `H` | `Shift+H` |
| Subtitles earlier | `G` | `Shift+G` |
| Reset or set exactly | **Subtitles > Subtitle Delay** | **[ALL] > Subtitles > Subtitle Delay** |

Each press is 100 ms, up to 5 minutes either way (a subtitle cut for another
release can be out by minutes).

## Subtitle style

Settings, General, **Subtitle Style**: font, size, color, bold, outline,
shadow, background box, and **Raise from bottom**. It applies to text
subtitles; ASS and SSA keep their own style except the position.

## SubtitleCat.com (optional)

Alabaster can search [SubtitleCat.com](https://www.subtitlecat.com/) for a
subtitle and load it into a cell. It's an **opt-in plugin**, off by
default. Alabaster isn't affiliated with or endorsed by SubtitleCat.com and
bundles no account, key, cookies or subtitle files.

### Set it up

1. Sign up and sign in to SubtitleCat.com **in your web browser**.
2. In Alabaster, Settings, Streaming, **Cookies**: pick that browser (and
   profile if you use several).
3. Settings, Plugins, **SubtitleCat.com**: turn on **Enable SubtitleCat.com**.
   The **Sign up** and **Sign in** buttons there only open subtitlecat.com
   in your browser.

### Use it

1. Right-click a cell, **Subtitles > Find subtitles on SubtitleCat.com…**.
2. The search words come from the file name; edit them and press search.
   Opening the window doesn't contact the site.
3. Pick a result, then a language. Your subtitle languages come first.
4. Download. The `.srt` is saved next to the video when that folder can be
   written to, otherwise in `subtitles` in the [data folder](../reference/data-folder.md).
   An existing file of the same name isn't overwritten (`name-2.srt`). The
   subtitle is loaded into the cell.

### Translations

Turn on **Request translations** too, and the window can ask SubtitleCat.com
to translate a subtitle into another language. One click is one request,
never retried. The site's reply (including a limit or VIP message) is shown
as it was sent; when it's a subtitle, a second click downloads it.

### Privacy

- Nothing is sent until you click a button, one request at a time, at least
  a second apart.
- Only your browser's `subtitlecat.com` cookies are used, for that one
  request, and never saved.
- With no browser picked, or no SubtitleCat.com login in it, the window says
  so and sends nothing.
- With the plugin off, its code isn't even loaded.
