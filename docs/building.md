# Building from source

## Requirements

- [uv](https://docs.astral.sh/uv/) (the project uses the `uv_build` backend and `uv.lock`)
- Python 3.10 or newer
- [VLC](https://www.videolan.org/)
- Optional: [just](https://github.com/casey/just) for the build recipes
- Optional: Deno, used by the bundled yt-dlp for YouTube; on Windows,
  `scripts/fetch_deno_windows.ps1` fetches it into `vendor/deno`
  (see `vendor/deno/README.md`).

## Run from source

```bash
uv sync
uv run gridplayer
```

On Windows you can also start `.\.venv\Scripts\gridplayer.exe`.

## Packages

The `justfile` has the build recipes, for example:

| Recipe | Builds |
| --- | --- |
| `just build` | wheel and sdist (`uv build`) |
| `just build-win-package` | Windows PyInstaller build and packages |
| `just build-linux-appimage` | Linux AppImage |
| `just build-macos-package` | macOS DMG (x86_64) |

See `CONTRIBUTING.md` for the extra tools each one needs.

!!! note "To be written"
    A tested, step-by-step Windows package build is not written yet.

## Docs

This site uses MkDocs Material. It is not a project dependency; install it in
a separate environment:

```bash
python -m venv /tmp/mkdocs-venv
/tmp/mkdocs-venv/bin/pip install mkdocs-material
/tmp/mkdocs-venv/bin/mkdocs serve
```

The hotkeys page is generated: `python tools/gen_hotkeys_md.py`.
