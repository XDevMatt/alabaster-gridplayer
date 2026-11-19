# Bisect checks

`end_of_track_check.py` tells whether a cell set to When Finished = Next
File acts before its file ends (exit 0) or only after VLC has started the
file over (exit 1, the end-of-track blip). It needs no libVLC playback:
it runs the cell's own `time_changed` on the times VLC reports at the end
of a file. Use it with `git bisect run`:

```sh
git bisect start <bad> <good>
git bisect run sh -c 'PYTHONPATH=$PWD QT_QPA_PLATFORM=offscreen python scripts/bisect/end_of_track_check.py'
```

Copy the script outside the work tree first if the range goes back past
the commit that added it.

The real-app counterpart, on a folder of two files or more, is
`tests/real_app/scenarios/end_of_track.py`.
