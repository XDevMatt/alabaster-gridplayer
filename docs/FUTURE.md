# Future features

These features are **not in GridPlayer Alabaster yet**. They are listed so you
know what is planned. Nothing here works in the current version, and there is
no promised date.

## Favorite channels

- Save favorite YouTube (or other yt-dlp supported) channels in the app.
- When you pick a saved channel, Alabaster shows its latest 3 to 5 published
  videos.
- The video you choose plays as a stream in a cell.

Today you can get close to this by adding a channel or playlist link as a
[list](USER-GUIDE.md#7-lists-in-a-cell): yt-dlp reads it, and the List window
can sort by date published.

## Keep options

- A user interface for **Keep** (`E`): turn it on or off, and choose **copy**
  or **move**.

Today Keep always copies, works only in single mode, and has no settings. See
[Keep](USER-GUIDE.md#keep-e).

## Rename on disk (F2)

- Rename the playing file on disk with `F2`.

`F2` is unbound and reserved for this. `F4` is the older in-app title rename,
which does not touch the file and is marked for removal.

## Loudness

- Loudness work (evening out volume between videos) after the beta.

## Separate audio for fragmented streams

- Pair video and audio that a site serves as separate fragmented files
  (YouTube's DASH formats among them) using ffmpeg, so higher qualities can be
  played. ffmpeg and ffprobe are already listed as user-installed tools for
  this reason; no current feature runs them.

## PortableApps.com package

- Package the Windows portable as a PortableApps.com Format `.paf.exe` so it
  can be installed through the PortableApps.com Platform.
- Host that package publicly (for example a GitHub Release) and post a
  development test on the PortableApps.com beta testing forum. There is no
  direct upload to their store.
- Official catalog listing is their decision and is not guaranteed.

Today you can unzip the standalone Windows portable zip yourself. That zip is
not in PortableApps.com Format.

## Other ideas on the roadmap

These are listed in the project roadmap as next ideas. None is built.

- **Keep a copy of a stream**: Keep (`E`) for links, not only local files.
- **Streamlink as an opt-in plugin**, like SubtitleCat.com.
- **Preview on hover over the seek bar.**
- **Skip Other Orientation that keeps going** past its 10-file look-ahead.
- **Window to video size.**
- **Reset all settings** from the Settings window.

## Slated for removal

- **F4 Rename**: `F4` opens a dialog that changes a cell's title and overlay
  color in the app. It never renames the file. It comes from upstream
  GridPlayer and is marked for removal from Alabaster.
