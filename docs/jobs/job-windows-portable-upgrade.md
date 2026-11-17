# Job: Windows portable upgrade tool

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** high.
**Branch from:** `main` is fine. New branch, for example
`feat/portable-upgrade`. Do not merge, tag, or release.

## Goal

An **in-app** action — for example a Help or Settings button labelled
**Upgrade from portable zip...** — that upgrades the running
**GridPlayer Alabaster portable** folder to a new
`GridPlayer-Alabaster-<commit>-win64-portable.zip`. It is not for the
Inno installer, Chocolatey, or WinGet.

**Decided:** the deliverable is this in-app button, not a standalone
script. Earlier notes that mentioned a PS7 script were only to describe
the exact function (backup, SHA256, Recycle Bin, unzip, restore,
relaunch, rollback). A small helper / updater process is required
because the running app cannot replace its own folder; that helper is
not a user-facing tool.

The user picks the new zip (and its `.sha256` file) from the app. The
app does not download a build.

## Flow

1. The user chooses **Upgrade from portable zip...** and picks the new
   portable zip. The sidecar `*.zip.sha256` can default to the zip path
   plus `.sha256`.
2. The app shows a **preview list** of every planned action and path,
   then waits. Nothing is changed until the user confirms (for example
   an Upgrade / Go button). Never call this a "dry run" in the UI,
   code, comments, docs, or tests.
3. On go, while the app is still running:
   - **Back up** user data and settings to a timestamped zip (details
     below).
   - **Verify SHA256** of the new portable zip. Refuse to continue if
     the hash is missing or does not match. Do not hand off, recycle,
     or unpack on a hash failure. If a data backup was already written,
     leave it in place and show its path.
   - **Hand off** to a small helper / updater process, then exit (or
     let the helper wait until this process has exited).
4. The helper / updater then, in this order:
   - **Wait** until the Alabaster process from this portable folder has
     actually exited. Match on the portable folder path. The program
     file is `GridPlayer.exe`, the same name as upstream GridPlayer.
     Never stop a `GridPlayer.exe` whose path is under
     `C:\Program Files\GridPlayer` or any other folder.
   - **Recycle** the old portable folder: send it to the Recycle Bin;
     do not permanently delete it. "Delete" in this project means
     Recycle Bin. Use the Windows shell (for example
     `Microsoft.VisualBasic.FileIO.FileSystem.DeleteDirectory` with
     `SendToRecycleBin`, or a documented equivalent that actually lands
     in the Recycle Bin). This is the `GridPlayer-Alabaster-portable`
     folder (or whatever folder contains this copy's `GridPlayer.exe`,
     `lib`, `libVLC`, and `portable_data`).
   - **Unzip** the new portable into the same parent install folder so
     `GridPlayer-Alabaster-portable\GridPlayer.exe` ends up where it
     was. The official zip name is
     `GridPlayer-Alabaster-<7-char-commit>-win64-portable.zip`, built
     by `scripts/windows/build_portable.py`. The sidecar `*.zip.sha256`
     is one line: `<hex>  <zip file name>`. The zip's top-level folder
     is `GridPlayer-Alabaster-portable\` (paths are stored relative to
     the stage parent).
   - **Restore** the backed-up `portable_data` (and any
     `GP_USER_DATA_DIR` data) so the new tree uses the user's settings,
     not the empty `portable_data` from the zip.
   - **Relaunch** `GridPlayer.exe`. Treat a failure to start as a
     failed install.
   - **Roll back** from the backup zip on failure (and put the previous
     portable folder back from the Recycle Bin if needed). If unpack,
     restore, or launch fails: restore, then stop. Leave the data
     backup in place even on success, and show its path.

The upgrade applies only to the running portable folder (the folder
that contains this process's `GridPlayer.exe`). Do not ask the user to
name a different portable directory.

### Backup details

For a portable install the data is `portable_data` next to
`GridPlayer.exe` (settings, playlists the app keeps there, logs, and
that folder's cache). If `GP_USER_DATA_DIR` is set, back that directory
up too. Do not skip this because the new zip already contains an empty
`portable_data`. Put the backup *outside* the folder you are about to
recycle (for example next to the parent install folder). Name it with a
local timestamp, for example
`GridPlayer-Alabaster-data-2026-11-17-1258.zip`.

## Preview list (required)

The preview list must show every planned action and path before any
change: which process will exit, which data folder will be zipped and
where, which folder will go to the Recycle Bin, which zip will be
hashed and unpacked, and where settings will be restored. Default is to
show the preview list and do nothing until the user confirms in the
app.

## Hard limits

- **Never touch** `C:\Program Files\GridPlayer` (upstream / Vlad's
  GridPlayer), its uninstall key, its settings under
  `%APPDATA%\vzhd1701\GridPlayer`, or its process.
- **Never touch** an Inno / Chocolatey install at
  `C:\Program Files\GridPlayer Alabaster\` or its uninstall key
  `{5E9EFBF1-5CB1-4898-BF59-6CA87176891D}`. This tool is portable
  only.
- Never recycle a folder that does not look like an Alabaster
  portable (must have `GridPlayer.exe` and a sibling `portable_data`
  or the usual `lib` / `libVLC` layout, and must not be under
  `C:\Program Files\GridPlayer`).
- If two Alabaster portables exist, only the running folder is in
  scope.
- Do not register file associations, write uninstall entries, or
  require Administrator. The portable does not install that way
  (`scripts/windows/PORTABLE-README.txt`).
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.

## Implementation notes

The helper can be a small process the app launches (an exe, or a
private PS7 helper that the user never has to run by hand). It is not
a standalone upgrade script, and it is not the product. Closing /
waiting for the app: follow the idea in
`packaging/chocolatey/tools/chocolateybeforemodify.ps1` (match
`GridPlayer` processes by path prefix), but use the portable folder,
not Program Files. Wait until the process has actually exited before
recycling.

## Tests

Prefer tests that run on the box and on Windows without needing a
real VLC or the full app:

- Preview list on a fake portable folder + zip + sha256 fixture
  shows the expected exit / backup / recycle / unpack / restore
  paths and leaves the folder bytes unchanged until confirm.
- Confirm with a matching sha256: data backup zip exists outside the
  recycled tree, new files are unpacked, `portable_data` from before
  is what the new tree has (not the empty one from the zip), and the
  new exe is launched.
- Confirm with a wrong or missing sha256: no hand-off, no recycle, no
  unpack, original folder untouched. A data backup zip may already
  exist if backup ran before verify; leave it in place and do not
  treat that as a successful upgrade.
- A fixture at `C:\Program Files\GridPlayer` (or a mocked path
  representing it) is never listed for recycle or close, even if a
  `GridPlayer.exe` is there.
- `C:\Program Files\GridPlayer Alabaster` is also out of scope.
- Failed unpack or failed launch after recycle: old folder is
  restored, data backup still exists.
- UI / comments / output / tests never contain the words "dry run".
- The upgrade entry point is an in-app control (Help or Settings),
  not a user-facing standalone script.

Pester is fine on Windows for helper behaviour. On the Linux box, test
the preview-list planning and hash check in Python if you extract that
logic, or skip the Recycle Bin cases with a clear marker. Do not
require TOUCHME or TOUCHMETWO.

## Files to read first

- `scripts/windows/build_portable.py` — zip name, top-level folder
  `GridPlayer-Alabaster-portable`, sha256 line format, empty
  `portable_data`
- `scripts/windows/PORTABLE-README.txt` — how the portable is laid out
- `gridplayer/utils/app_dir.py` — `portable_data`, `GP_USER_DATA_DIR`,
  roaming fallback `%APPDATA%\vzhd1701\GridPlayer-Alabaster` (only if
  `portable_data` is missing; a normal portable has that folder)
- `packaging/chocolatey/tools/chocolateybeforemodify.ps1` — close by
  path, not by exe name alone
- `scripts/windows/installer.iss` — installer folder and AppId, so you
  know what *not* to touch

## Constraints

- Windows-only. No macOS / Linux packaging.
- No merge, tag, or release. Do not publish a package.
- Never say "dry run".
- Do not use Jules or Antigravity.
- Recycle Bin, not permanent delete, for the old portable folder.
- The user-facing deliverable is the in-app button, not a standalone
  script.
