# Job: Windows portable upgrade tool

**Resource:** Grok Build (multi-file coding).
**Size:** medium.
**Priority:** high.
**Branch from:** `main` is fine (scripts only). New branch, for example
`feat/portable-upgrade`. Do not merge, tag, or release.

## Goal

A PS7 script, and if it stays small an in-app action that calls it, that
upgrades an existing **GridPlayer Alabaster portable** folder to a new
`GridPlayer-Alabaster-<commit>-win64-portable.zip`. It is not for the
Inno installer, Chocolatey, or WinGet.

The user points it at the new zip (and its `.sha256` file). It does not
download a build.

## Steps (in this order)

1. **Close running Alabaster** from this portable folder only. The
   program file is `GridPlayer.exe`, the same name as upstream
   GridPlayer. Match on the portable folder path. Never stop a
   `GridPlayer.exe` whose path is under `C:\Program Files\GridPlayer`
   or any other folder.
2. **Zip the user data** to a timestamped backup. For a portable
   install the data is `portable_data` next to `GridPlayer.exe`
   (settings, playlists the app keeps there, logs, and that folder's
   cache). If `GP_USER_DATA_DIR` is set, back that directory up too.
   Do not skip this because the new zip already contains an empty
   `portable_data`. Put the backup *outside* the folder you are about
   to recycle (for example next to the parent install folder, or in a
   folder the user passed). Name it with a local timestamp, for
   example `GridPlayer-Alabaster-data-2026-11-17-1258.zip`.
3. **Recycle the old portable folder.** Send it to the Recycle Bin; do
   not permanently delete it. "Delete" in this project means Recycle
   Bin. Use the Windows shell (for example
   `Microsoft.VisualBasic.FileIO.FileSystem.DeleteDirectory` with
   `SendToRecycleBin`, or a documented equivalent that actually lands
   in the Recycle Bin). This is the `GridPlayer-Alabaster-portable`
   folder (or whatever folder contains this copy's `GridPlayer.exe`,
   `lib`, `libVLC`, and `portable_data`).
4. **Verify SHA256, then unzip** the new portable into the same parent
   install folder so `GridPlayer-Alabaster-portable\GridPlayer.exe`
   ends up where it was. The official zip name is
   `GridPlayer-Alabaster-<7-char-commit>-win64-portable.zip`, built by
   `scripts/windows/build_portable.py`. The sidecar
   `*.zip.sha256` is one line: `<hex>  <zip file name>`. Refuse to
   unpack if the hash is missing or does not match. The zip's top-level
   folder is `GridPlayer-Alabaster-portable\` (paths are stored
   relative to the stage parent).
5. **Restore settings, launch-check, roll back on failure.** Copy the
   backed-up `portable_data` (and any `GP_USER_DATA_DIR` data) back so
   the new tree uses the user's settings, not the empty
   `portable_data` from the zip. Then start `GridPlayer.exe` and treat
   a failure to start as a failed install. If verify, unpack, restore,
   or launch fails: put the previous portable folder back from the
   Recycle Bin, restore data from the timestamped zip if needed, and
   stop. Leave the data backup in place even on success, and print its
   path.

## Preview list (required)

A **preview list** mode prints every planned action and path, then
exits without changing anything: which process would be closed, which
data folder would be zipped and where, which folder would go to the
Recycle Bin, which zip would be hashed and unpacked, and where
settings would be restored.

Never call this a "dry run" in the script, its help, comments, docs,
or tests. The flag should be something like `-PreviewList` or
`-Preview`. Default is to show the preview list and do nothing until
the user also passes an explicit confirm flag (for example
`-Apply`). Do not recycle or unpack without that confirm flag.

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
- If two Alabaster portables exist, only the folder the user named is
  in scope.
- Do not register file associations, write uninstall entries, or
  require Administrator. The portable does not install that way
  (`scripts/windows/PORTABLE-README.txt`).
- Identity is XDevMatt only. Never write the maintainer's personal
  name, handles, or personal email; use `<user>` if a placeholder is
  required.

## Suggested interface

PS7 script, for example `scripts/windows/Upgrade-AlabasterPortable.ps1`:

```powershell
# Preview list only (no changes):
#   pwsh -File Upgrade-AlabasterPortable.ps1 -PortableDir 'D:\apps\GridPlayer-Alabaster-portable' -NewZip 'D:\downloads\GridPlayer-Alabaster-abc1234-win64-portable.zip' -PreviewList

# Apply:
#   pwsh -File Upgrade-AlabasterPortable.ps1 -PortableDir 'D:\apps\GridPlayer-Alabaster-portable' -NewZip 'D:\downloads\GridPlayer-Alabaster-abc1234-win64-portable.zip' -Apply
```

`-Sha256File` can default to the zip path plus `.sha256`.
`-BackupDir` can default to the parent of `-PortableDir`.

Closing processes: follow the idea in
`packaging/chocolatey/tools/chocolateybeforemodify.ps1` (match
`GridPlayer` processes by path prefix), but use the portable folder,
not Program Files. Wait until the process has actually exited before
recycling.

In-app action (optional in this job if the script is solid): a menu
item that asks for the new zip and runs the script with `-PreviewList`
first, shows that list, then asks before `-Apply`. If that part grows,
land the script first and leave the menu item for a follow-up rather
than stalling.

## Tests

Prefer tests that run on the box and on Windows without needing a
real VLC or the full app:

- Preview list on a fake portable folder + zip + sha256 fixture
  prints the expected close / backup / recycle / unpack / restore
  paths and leaves the folder bytes unchanged.
- Apply with a matching sha256: data backup zip exists outside the
  recycled tree, new files are unpacked, and `portable_data` from
  before is what the new tree has (not the empty one from the zip).
- Apply with a wrong or missing sha256: no recycle, no unpack, data
  untouched, non-zero exit.
- A fixture at `C:\Program Files\GridPlayer` (or a mocked path
  representing it) is never listed for recycle or close, even if a
  `GridPlayer.exe` is there.
- `C:\Program Files\GridPlayer Alabaster` is also out of scope.
- Failed unpack or failed launch after recycle: old folder is
  restored, data backup still exists, script exits non-zero.
- Help / comments / output never contain the words "dry run".
- The script is PS7 (`pwsh`), not Windows PowerShell 5, if it uses
  syntax that needs PS7.

Pester is fine on Windows. On the Linux box, test the preview-list
planning and hash check in Python if you extract that logic, or skip
the Recycle Bin cases with a clear marker. Do not require TOUCHME or
TOUCHMETWO.

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
