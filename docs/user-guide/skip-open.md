# Skip files open elsewhere

When several cells play from the same folder or list, **Play Random File**
(`Shift+N`, or When Finished set to **Play random file**) avoids files that
are already open in another cell, so you don't see the same clip twice on
screen.

- It's on by default: Settings, Defaults, Playlist, Folder Navigation,
  **Skip files open in other cells**.
- It works for folder stepping and for [lists](lists.md).
- It applies to **Random only**. Next and Previous (`N` / `B`) go in order
  and can land on a file another cell is playing.
- "When it can": if every remaining file is open somewhere, one of them
  plays anyway.
- Only local files count; links aren't compared.
