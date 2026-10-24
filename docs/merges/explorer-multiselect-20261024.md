# Explorer multi-select and folders: one window, a cell per file, a cell per folder

Branch `folder-cell-20261024`, from master `cba4adb`.

## What was asked

Files and folders picked together, however they come in (Explorer's right-click
menu, drag-n-drop, the Add Files / Add Folder / Add URL(s) dialogs, a paste, the
command line), go into one window: one cell for each file, one cell for each
folder that plays the folder as a list. This is the default for a new player.

## What was there already

- Every in-app path ends in `AddVideosManager.add_media`
  (`gridplayer/player/managers/add_videos.py`): Add Files (`cmd_add_videos`), Add
  Folder (`cmd_add_folder`), Add URL(s) (`cmd_add_urls`), paste
  (`cmd_add_from_clipboard`), drag-n-drop (`drag_n_drop._drop_files`), Recent
  (`recent_list`), and the command line and files forwarded from a second start
  (`playlist.process_arguments`). They all place cells the one way, by
  `playlist/add_mode`.
- `playlist/add_mode` defaults to `cell_each`, "One per item" in Settings: a cell
  for each file, one for each folder or playlist, playing it as a list. That is
  the rule asked for, and already the default for a new player.
- "One for all" (`one_cell`) puts everything added together into one cell. A
  player set to it merges files picked in a dialog, pasted or dropped together.
  To get the rule above, set Settings, Drag-n-Drop, Cells, to "One per item" (or
  `[playlist] add_mode=cell_each` in `settings.ini`).
- Explorer starts one player for each item picked. Each start hands its one item
  to the running player, which puts each in a cell of its own whatever
  `add_mode` says. A dropped `.gpl` opens as a playlist (it replaces the grid);
  that is not an add.

## The bug: more than one window

Measured on Linux with N players started at once, the way Explorer starts them
(`player/one_instance` on, the default):

| started at once | before | after |
|---|---|---|
| 5 files | 1 window, 5 cells | 1 window, 5 cells |
| 10 files | 2 windows (9 + 1 cells) | 1 window, 10 cells |
| 12 files + 1 folder | more than one player left running, every run | 1 window, 12 cells + 1 list cell, every run |
| 15 files, `one_cell` | | 1 window, 15 cells |

Causes, in `gridplayer/utils/single_instance.py`:

- Linux: a second start pinged the socket and, if the ping failed, took it for a
  dead player's, deleted it and became a first player itself. A first player
  still starting (bound but not yet listening, or with its backlog of 16 full of
  pings and files) failed the ping, so several became first.
- Windows (by reading the code; not run here): the pipe takes one client at a
  time, and the first player only starts taking them once its window is up. A
  second start waited 2 s (`CLIENT_CONNECT_TIMEOUT_S`, from the exit-hang fix),
  then gave up and opened a window of its own, without a listener. A cold
  `pythonw` start with a dozen files picked easily takes longer than that.

## The fix

- Linux: the first player is the one holding a POSIX lock on
  `<socket>.lock` (`_take_primary_lock`). The lock goes with the process however
  it ends and is not held by the processes it starts, so a crashed player's
  leftover socket is taken over at once and a player still starting is never
  taken for a crashed one. The ping is gone. The backlog is 128.
- Both: a second start keeps trying to hand its files over for up to 20 s
  (`DELEGATE_TIMEOUT_S`) while the first player is starting or busy with the
  others, then opens its own window as before, with a warning in the log. On
  Windows a pipe that is not there at all is a player gone, and is not waited
  on. The listener's own shutdown message still waits at most 2 s.

## Tests

- `tests/test_instance_election.py` (Linux): one first player out of 8 started
  at once; a crashed player's socket is taken over; a second start hands its
  files to a first one that only starts listening after 1 s; gives up on one
  that never listens; becomes first once the first one is gone.
- `tests/test_add_media.py::TestEveryWayInAddsAlike`: Add Files, Add Folder, Add
  URL(s), paste, drop, command line, and one start a file under the default, plus
  one start a file under `one_cell`.
- `tests/real_app/test_explorer_multiselect.py`: 12 files and a folder started as
  13 players at once, under the default and under `one_cell`: one player left,
  one window, 12 single cells and one cell playing the folder's 3 files. Fails
  on master every run, passes on this branch (5 of 5 runs).

## Not done

- Cells from Explorer come in the order the starts reach the player, not
  Explorer's order.
- No `--folder-cell` flag: a folder on the command line already plays in one
  cell under every mode but "One per video".
- The Windows pipe path has no Windows run here.
