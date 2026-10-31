# Where things are stored

## Settings file

Settings are kept in a Qt `QSettings` INI file, `settings.ini`:

- Windows: `%APPDATA%\vzhd1701\GridPlayer-Alabaster\settings.ini`
- Other systems: the Qt application data folder for `vzhd1701/GridPlayer-Alabaster`.

The folder is Alabaster's own; upstream GridPlayer uses `...\vzhd1701\GridPlayer`.

The data folder is chosen in this order:

1. `--user-data-dir <folder>` on the command line, or the `GP_USER_DATA_DIR`
   environment variable.
2. Portable mode: a `portable_data` folder next to the program (Windows
   packaged build only).
3. The normal location above.

## Registry (Windows)

Nothing is written to the registry. Two things are only read:

- `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme`
  (for the System color scheme).
- Where VLC is installed.

## Playlists

Playlists are `.gpls` files written as JSON (older text-format playlists can
still be read).

More detail: [Settings reference](settings-reference.md#where-settings-are-kept).
