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
   - **Carry over user content only.** The new portable starts with
     **default app settings**: the empty `portable_data` from the zip is
     kept, and the old `settings.ini`, `media_shapes.json`, and logs are
     **not** restored (they stay in the backup zip). Copy into the new
     tree only user content found by the scan (below): `.gpls`
     playlists, downloaded subtitles (for example
     `portable_data\subtitles\`), and other user-created files that
     were not in the old zip. Anything the scan marks unclear is listed
     for the user's call and not copied until they say so.
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

**Decided (2026-11-18):** back up the old config, do not restore it.
The new portable runs on default settings; most per-grid settings live
in the user's `.gpls` playlists, which are kept.

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
where, the measured user-content size and file count, any flagged
items (caps, links, unclear files), which folder will go to the
Recycle Bin, which zip will be hashed and unpacked, which user files
will be carried over, and that app settings start at defaults.
Default is to
show the preview list and do nothing until the user confirms in the
app.

## Safety caps and link safety (required)

The scan that decides what to back up and carry over must stop and ask
(list it in the preview list, copy and recycle nothing) instead of
acting when any of these hold. Measure first, then decide.

**Size caps (user content only, stock files from the old zip excluded):**

- Total user content over **~200 MB**.
- More than **~500** user files.
- Any single file over **50 MB** (likely media that should not be in
  the app folder).

Show the measured total size and file count in the preview list either
way. Those sizes mean a storage drive, a cross-linked folder, or a
portable unzipped into Downloads, not app data.

**Folder sanity:** stop and ask, and do not scan or copy, if the old
portable folder is (or is directly) a shared/user folder: Downloads,
Desktop, Documents, Pictures, Videos, Music, the user profile root
itself, OneDrive roots, or a drive root (`C:\`, `D:\`, ...). The
portable must be its own folder that contains `GridPlayer.exe`,
`lib`, `libVLC`, and `portable_data`.

**Links (never follow):**

- Detect symlinks **and** junctions by the reparse-point attribute
  (`FILE_ATTRIBUTE_REPARSE_POINT`, from `os.lstat(...).st_file_attributes`;
  `Path.is_junction()` on Python 3.12+ as a cross-check). Never descend
  into, copy through, or recycle through a reparse point. Use
  `os.walk(followlinks=False)` / `lstat`, never `stat`, and prune
  reparse-point directories before descending. List each one found.
- Detect hard links by `st_nlink > 1` on each file. Flag them; do not
  copy them, and never recycle a hard-linked file (or a folder that
  contains one) without asking, because recycling one name changes what
  the other names point at.
- If any reparse point or hard link is found, the upgrade stops at the
  preview list and asks. It does not recycle the old folder.

**Acceptance requires automated tests** (Windows; skip with a clear
marker elsewhere) that build a fixture portable folder containing, all
pointing at an outside folder with sentinel files:

1. a file symlink,
2. a directory symlink,
3. a junction (`mklink /J` or `_winapi.CreateJunction`),
4. a hard link (`os.link`).

The tests must prove the scan flags all four, the backup zip and the
carry-over copy contain nothing reached through them, nothing is
recycled, and the outside folder's sentinel files are unchanged
afterwards. Add fixtures for each size cap (200 MB total can use
sparse files or a lowered cap injected for the test, 500 files, one
file over 50 MB) and for each shared-folder case, proving the tool
stops at the preview list. Link and cap safety counts as verified only
by these tests passing, not by inspection.

## Working rules: steps and checkpoints (required)

Work in the numbered steps below, in order. Each step ends at a
checkpoint built for a context reset:

1. Run the tests named in the step plus the existing suite for the
   files touched; they must pass.
2. Commit (XDevMatt identity) with the step number in the message, for
   example `step 3: ...`.
3. Append an entry to `docs/progress/<job-name>.md` on the work branch:
   step number, what is done, what is next, which tests pass (command
   and count), and any open question. A fresh session must be able to
   continue from that note and `git log` alone.

Rules for every step:

- **No behaviour changes outside the step's stated scope.** If
  something else looks wrong, write it in the progress note; do not fix
  it in this step.
- Every step states **what behaviour it changes** (or "none" for a
  pure refactor or a test-only step).
- Every step that changes behaviour adds a **before/after regression
  test**: it fails on the commit before the step and passes after it.
  A refactor step proves "no change" with the existing tests passing
  unchanged.
- Steps stay small: one reviewable commit each. Split a step that grows.

## Steps

1. **Planner (pure logic, no side effects).** Given the running
   portable folder, the new zip, and its `.sha256`, build the preview
   list: process to exit, data backup target, measured user-content
   size and file count, flagged items (caps, links, shared folders,
   unclear files), folder to recycle, zip to unpack, user files to
   carry over, and "app settings start at defaults". Tests on fixture
   folders. *Behaviour change: none (not wired).*
2. **Link and cap safety in the scanner**, with the four-link fixture
   tests and the cap / shared-folder tests from **Safety caps and link
   safety**. *Behaviour change: none (not wired).*
3. **Backup + SHA256 verify** (writes only the backup zip outside the
   portable). Tests: matching, wrong, and missing hash.
   *Behaviour change: none in the app yet.*
4. **Helper process**: wait for exit by path, recycle, unpack, carry
   over user content (not config), relaunch, roll back on failure.
   Tests with fixtures; Recycle Bin cases skipped with a marker off
   Windows. *Behaviour change: none until wired.*
5. **In-app button** (Help or Settings) that shows the preview list and
   runs steps 3-4 on confirm. *Behaviour change: new menu action.*
   Before/after test that the action exists and does nothing until
   confirm.
6. **Real-app check** on Windows with two real portable zips, result in
   the progress note.

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
  recycled tree and holds the old `portable_data`; new files are
  unpacked; the new tree's `settings.ini` is the default one (old
  settings are **not** restored); `.gpls`, downloaded subtitles, and
  other user files from the scan are carried over; the new exe is
  launched.
- The safety-cap and link-safety tests in **Safety caps and link
  safety** above.
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
