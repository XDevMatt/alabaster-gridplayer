# Pictures (new in 0.2beta)

Pictures play as slides: each one is shown for the cell's **Slide duration**,
then the cell's **When Finished** action runs, just as at the end of a video.
An animated GIF plays as VLC plays it.

Supported extensions: `jpg`, `jpeg`, `jpe`, `jfif`, `png`, `webp`, `gif`,
`bmp`, `tif`, `tiff`.

## Slide duration

From 1 to 3600 seconds, default 10.

## Files to Play

Chooses what a cell plays when it steps through a folder:

- **Videos only** (default)
- **All media** (videos, audio and pictures)
- **Images only**

It can be set per cell and for all cells (`[ALL]`). A picture you drop on the
window is still opened, whatever this is set to.
