# FAQ and troubleshooting

!!! note "To be written"
    More questions will be added.

## How do I run it from source?

From the repository folder, after `uv sync`:

```powershell
.\.venv\Scripts\gridplayer.exe
```

## I typed `gridplayer` and got an old version

If GridPlayer 0.5.3 (or another upstream version) is installed, the
`gridplayer` command on PATH may start that program. It is a different program
from Alabaster, with its own settings. Run the one in `.\.venv\Scripts\`
instead.
