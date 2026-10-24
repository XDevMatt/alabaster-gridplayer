# Alabaster to-do


- [ ] 2026-10-23: Multi-file open. Opening several video files at once did not land them all in one Alabaster instance, even with one_instance=True. Check: Explorer multi-select Enter/Open (one %1 per file, sent to the running instance via the pipe), drag-and-drop (OLE) onto the window and onto cells (drop where you see it, WYSIWYG), and timing races when many launches arrive together.

- [ ] 2026-10-23: Tray icon says GridPlayer. Give Alabaster its own tray name and tooltip (and a visually distinct icon) so it isnt confused with legacy GridPlayer.

- [ ] 2026-10-23: System volume slider jumps and settles only every 10-20 points while Alabaster is running (the maintainer test). Alabaster has no global mouse/keyboard hooks; on Windows it forces VLC --aout=directsound (instance.py, from upstream), one DirectSound stream per cell. Test: slider with Alabaster closed vs open with 1 and 4 playing cells, on Vizio BT (absolute volume on) and on Realtek. Try --aout=mmdevice (WASAPI) as an opt-in setting.
