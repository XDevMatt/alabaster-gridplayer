# Loops

## A-B loop

| Action | Cell under cursor | All cells |
| --- | --- | --- |
| Set Loop Start (A) | `[` | `Shift+[` |
| Set Loop End (B) | `]` | `Shift+]` |
| Loop Reset | `\` | `Shift+\` |

In Alabaster, `[` and `]` set loop points; they no longer seek -5% / +5% as in
upstream GridPlayer.

## Loop This File

`Shift+L` toggles a cell between **Loop This File** and its previous When
Finished action.

It's the same as picking **Playback > When Finished > Loop This File**, and
back. When Finished set from the menu has nothing to go back to, so Shift+L
then just says the file loops.

## Random Loop

**Playback > Loop > Random Loop** (no default key): each pass of the loop,
or of the file, starts somewhere at random instead of at the loop start. For
every cell: **[ALL] > Playback > Loop > Random Loop > On / Off**. The New
Videos default is **Start at random position** (off). Live streams never loop.

## Loop Chapter

**Playback > Loop > Loop Chapter** (no default key) sets the A-B loop to the
chapter that's playing, for files with chapters. **Loop Reset** clears it.

## Where loops are kept

Loop points are per cell and saved with the playlist. Moving to another file
(Next, Previous, Random) clears the loop.

## When finished

**Playback > When Finished** decides what happens at the end of a file:

| Choice | Result |
| --- | --- |
| **Loop This File** (default) | Start again. |
| **Play Next File** / **Play Previous File** | Go to the next or previous file of the folder or list. |
| **Play Random File** | Go to a random file (no repeats until all have played). |
| **Pause At Start** | Go back to the start and pause. |
| **Stop** | Stop. |
| **Close** | Close the cell. |

For a picture, When finished runs after the **Slide duration**.

VLC can log a seek to 0% each time an Ogg/Opus file loops. It is log noise;
see [Known limitations](../KNOWN-LIMITATIONS.md).
