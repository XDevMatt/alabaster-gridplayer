# Keep (`E`)

Keep is for sorting through a folder: watch a file, press `E` if it's a
keeper, and Alabaster copies it aside and plays the next one.

## Use it

1. Double-click a cell to enter **Single Mode** (the grid needs at least two
   cells or places for Single Mode to be offered).
2. While a local file you want plays, press `E` (or right-click, **File > Keep**).

Alabaster then:

- **copies** (never moves) the file into a folder named after its own
  folder plus `_keep`, next to that folder;
- **skips the copy** if a file with that name is already there;
- **plays the next file** in the cell, the same as `N`.

Example: keeping `D:\clips\beach\IMG_0042.mp4` copies it to
`D:\clips\beach_keep\IMG_0042.mp4`. The `beach_keep` folder is made the
first time.

## Good to know

- **Single Mode only.** In the grid, `E` does nothing and **Keep** isn't on
  the menu.
- **Local files only.** Links and streams can't be kept (a stream version is
  on the [roadmap](../FUTURE.md)).
- **No overwrite.** An existing file of the same name in the `_keep` folder
  is left alone, even if it's different.
- **Quiet.** There's no message on screen. A failed copy (a full disk, a
  read-only drive) is written to the log, and the cell still moves on to
  the next file. If you need to be sure, check the `_keep` folder.
- **Next only where there is one.** A cell playing a folder or a list moves
  on; a cell with nothing to step through stays on the file.
- The original file is never touched.
- `E` can be changed on the Shortcuts page (action **Keep**).

!!! note "Changed from earlier builds"
    Earlier test builds put Keep on `K`. `K` is audio delay again (see
    [Audio](audio.md)); Keep is `E`.
