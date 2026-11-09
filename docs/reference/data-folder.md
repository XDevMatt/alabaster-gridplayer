# Data folder and portable mode

Alabaster keeps its settings, log, screenshots and a few caches in one
**data folder**. To open it: Settings, **Open data folder** (bottom of the
window).

## Where it is

Alabaster picks the first of these that applies:

1. **`--user-data-dir PATH`** on the command line, or the
   **`GP_USER_DATA_DIR`** environment variable (the option wins). Relative
   paths are from the current folder.
2. **Portable mode**: a folder named `portable_data` next to `GridPlayer.exe`
   (the packaged Windows app only). The portable ZIP ships with it.
3. **The normal place**:
   `C:\Users\<user>\AppData\Roaming\vzhd1701\GridPlayer-Alabaster\`

The `vzhd1701` part comes from upstream GridPlayer. Upstream uses
`...\vzhd1701\GridPlayer\`, so the two never share settings.

## What's in it

| File or folder | What |
| --- | --- |
| `settings.ini` | All settings. Changed shortcuts are stored as differences from the defaults. |
| `gridplayer.log` | The log. |
| `screenshots\` | Screenshots, unless you set another folder. |
| `subtitles\` | SubtitleCat.com downloads that couldn't go next to their video. |
| `media_shapes.json` | Which files are portrait or landscape, remembered for the aspect filter. |
| `cache\` | Thumbnails and downloaded lists, **only** in portable mode or with a custom data folder. |

Otherwise the cache goes in Windows' local cache location
(`C:\Users\<user>\AppData\Local\vzhd1701\GridPlayer-Alabaster\cache\`), which
backups and roaming profiles skip. Settings, General, Player, Cache: keep
it **On disk** (default, up to 1024 MB) or **In memory** (up to 32 MB,
cleared on exit; switching deletes the disk cache).

## Portable mode

- Settings, logs, screenshots and cache all stay inside `portable_data`.
  Nothing is written to `AppData`.
- Move or copy the whole `GridPlayer-Alabaster-portable` folder and your settings go with it.
- Delete `portable_data` (or run the installed app) to use the normal place.

## Playlists

Saved playlists are `.gpls` files, wherever you save them. Alabaster writes
them as JSON; older GridPlayer text playlists still open.

## Registry

The app itself writes nothing to the registry. It reads the Windows light /
dark setting for the **System** color scheme. The installer (not the app)
adds the uninstall entry, Start menu shortcuts and file associations.
