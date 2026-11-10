# 0.2beta release checklist

What is left before GridPlayer Alabaster 0.2beta goes out. Nothing here is
done by an agent without the maintainer's go: no tags, no releases, no merges to
master.

## Version string

- [x] `gridplayer/version.py`: `__fork_version__` is `0.2beta_rc1`
      (About shows this), matching the current prerelease tag.
- [ ] `pyproject.toml` `version = "0.5.5"`: keep as the upstream base or
      move to the fork's version; match whatever version.py says.
- [ ] `NOTICE`: "Fork version" and the "Modified" date range (still says
      2026-10-14 to 2026-10-23).
- [ ] `scripts/init_app_vars.sh`: `APP_REPO_SLUG` is still
      `vzhd1701/gridplayer` (used for the CDN and release URLs).
- [ ] Windows file version (`scripts/pyinstaller/version_info.py`) and the
      Chocolatey nuspec (`packaging/chocolatey/*.nuspec`, 0.2.0-beta) agree.
- [ ] Tray name and notifications still say "GridPlayer" (audit B13).

## Changelog

- [ ] `CHANGELOG.md` has only upstream's `[Unreleased]` entries, linked to
      upstream commits. Add a `0.2beta` section for the fork: pictures as
      slides, Files to play, rotate-to-fit, aspect filter Skip it, snapshots
      fix, Include subfolders on by default, folder drops follow Files to
      play (B1), Skip files open in other cells on by default, grid Next
      repaint fix.

## README

- [ ] "Changes so far" leaves out the 0.2beta work (same list as above).
- [ ] The badges at the top (PyPI, downloads, Crowdin) point at upstream
      GridPlayer. Remove them or point them at the fork.
- [ ] Requirements: ffmpeg, yt-dlp and Deno are user-installed (already in
      the docs; check README says the same).

## License and attribution

- [ ] `LICENSE` is the unchanged GPL-3.0 text. Keep it.
- [ ] `NOTICE` names GridPlayer by vzhd1701 as the original work and lists
      the changes; extend the change list with 0.2beta.
- [ ] About dialog credits upstream (`__upstream_*` in version.py).
- [ ] The Windows build ships VLC (libVLC, LGPL/GPL): its license files go
      in the installer.
- [ ] Release notes say it is a modified version of GridPlayer 0.5.5.

## Build and installer

- [ ] Windows build: `just build-win-package` (PyInstaller, then
      `scripts/windows/installer.iss`). Installed copy on the maintainer's Windows PC is from
      2026-10-26 and predates all 0.2beta work; rebuild from the release
      commit.
- [ ] Install on a clean Windows (Sandbox or VM), check file associations,
      the single-instance pipe (`gridplayer-alabaster-fileopen`) and that it
      runs next to upstream GridPlayer with its own settings folder.
- [ ] Chocolatey: follow `packaging/chocolatey/README.md` (SHA256, pack,
      test install, push).
- [ ] CI: `.github/workflows/release_pypi.yml` publishes the `gridplayer`
      name to PyPI on a `vX.Y.Z` tag. A `v0.2.0-beta` tag does not match
      that pattern, but disable or rename that workflow before any plain
      version tag, so the fork never publishes under upstream's name.

## Tests before the tag

- [ ] `QT_QPA_PLATFORM=offscreen uv run pytest` on a machine with VLC
      (Linux box has no libVLC, so about 66 VLC tests only run on Windows).
- [ ] `uv run pytest -m real_app` on Windows (known flaky ones are listed
      in HANDOFF.md).
- [ ] Manual: drop a folder with mp3s and pictures under Videos only; press
      Next in a 2x2 grid of HW videos and watch the other panes.

## Open issue: grey panes on Next (B3)

Done in 0.2beta-fixes: in a grid, Next no longer repaints the whole window,
only the cell that moves on (single mode still repaints the window, which
it needs). That was the likely cause on Linux; on Windows it may not be the
whole story.

Not done, on purpose: making the old player's release non-blocking
(`VideoBlock._release_video_driver` waits up to 5 s for VLC to let go, on
the GUI thread). The release order there is deliberate (the paint has to be
in place before the hardware window goes), and freeing the window before
VLC is done with it can crash VLC. It needs a design and a test on Windows
first.

If panes still go grey on Windows, try first (10 minutes):

1. Settings, Videos per process = 1. If the greying stops, the shared
   decoder process is the cause (audit B7/B8).
2. Try the SP video driver instead of HW.
3. Look in `gridplayer.log` for "Timed out waiting for VLC player to
   release" and "Decoder process ... died".

## F4 Rename (in-app title only)

F4 `Rename` changes the displayed name inside the app only; it does not
rename the file on disk. If the cell is showing a full path, that edit can
look like `c:\movies\New Filename Dog Pee.mp4`, and after Next, Previous,
or Random the old title can stay stuck until a restart or playlist load.

- [ ] Before release: if no useful purpose is found, remove F4 Rename.
      The maintainer (2026-11-07): lose it before release unless we figure out a use;
      at minimum mark it for deletion here. A later disk rename belongs on
      unbound F2, not F4.

## Aspect filter Ask

Ask can prompt Play anyway / Skip when the next file is the other
orientation. The maintainer (2026-11-07) is not sure it still works well; he stopped
using it a while back when ignore needed heavy testing. Skip it is the mode
to call out.

- [ ] Before release: verify Ask still prompts Play anyway / Skip, or do
      not treat it as solid in the notes.
