"""Single mode stays on while the shown cell moves to another file.

The next file is put in the same cell. That must not turn single mode off
or show the cells it hides, not even for a moment while the old picture is
let go. A normal-size window is not resized on the way.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt5.QtCore import QEvent, QObject, QSettings, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.models.grid_state import GridState
from gridplayer.models.video import Video
from gridplayer.params.static import GridMode, VideoEndAction
from gridplayer.player.managers.grid import GridManager
from gridplayer.player.managers.single_mode import SingleModeManager
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.settings import Settings
from gridplayer.widgets.video_block import VideoBlock


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path):
    settings = Settings()
    real_settings = settings.settings
    settings.settings = QSettings(str(tmp_path / "test.ini"), QSettings.IniFormat)
    # one folder at a time; Include subfolders is on by default
    settings.set("video_defaults/dir_recursive", False)
    PlaylistSettings().clear()

    yield

    PlaylistSettings().clear()
    settings.settings = real_settings


class _Surface(QWidget):
    """A hardware surface as far as letting one go goes. No VLC."""

    is_native_surface = True
    video_ready = pyqtSignal()
    picture_shown = pyqtSignal()
    view_followed = pyqtSignal(object)
    tracks_changed = pyqtSignal()
    chapters_changed = pyqtSignal()
    time_changed = pyqtSignal(int)
    playback_status_changed = pyqtSignal(bool)
    error = pyqtSignal(str, tuple)
    crash = pyqtSignal(str)
    update_status = pyqtSignal(str, int)
    screenshot_taken = pyqtSignal(object, object)

    is_picture_pending = False
    is_live = False

    # filled in by the test, read while a surface is being let go
    cells = []
    notes = []

    def __init__(self, vlc_options=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self._initialized = True
        self.asked = []

    @property
    def is_video_initialized(self):
        return self._initialized

    def set_pause(self, paused):
        self.asked.append(bool(paused))

    def load_video(self, media):
        return None

    def cleanup(self):
        cell = self.parent()
        window = cell.window()
        others = [c for c in _Surface.cells if c is not cell]
        empties = [
            widget
            for widget in window.findChildren(QWidget)
            if getattr(widget, "is_empty_cell", False)
        ]
        _Surface.notes.append(
            {
                "filled": cell.autoFillBackground(),
                "shown": (cell.width(), cell.height()),
                "window": (window.width(), window.height()),
                "others_visible": [c.isVisible() for c in others],
                "empties_visible": [widget.isVisible() for widget in empties],
            }
        )


class _Shows(QObject):
    """Names of video cells and empty cells that become visible."""

    def __init__(self):
        super().__init__()
        self.names = []

    def eventFilter(self, obj, event):
        if event.type() != QEvent.Show:
            return False
        if obj in _Surface.cells or getattr(obj, "is_empty_cell", False):
            self.names.append(obj.objectName() or "empty")
        return False


class _Cells:
    def __init__(self, items):
        self._cells = items

    @property
    def video_ids(self):
        return [cell.video_id for cell in self._cells]

    def __bool__(self):
        return bool(self._cells)

    def __iter__(self):
        return iter(self._cells)

    def __len__(self):
        return len(self._cells)

    def by_video_id(self, video_id):
        return next((cell for cell in self._cells if cell.video_id == video_id), None)

    def blocks_for_ids(self, video_ids):
        return [
            self.by_video_id(video_id)
            for video_id in video_ids
            if self.by_video_id(video_id)
        ]


def _context():
    context = SimpleNamespace()
    context.is_drag_ui = False
    context.is_disable_overlay = True
    context.is_overlay_hide_on_timeout = False
    context.is_show_overlay_border = False
    context.overlay_timeout = 1
    context.is_disable_mouse_wheel_events = False
    context.is_disable_mouse_click_events = False
    context.lists = MagicMock()
    context.lists.get.return_value = None
    context.lists.is_waiting.return_value = False
    context.bookmarks = MagicMock()
    return context


def _video(folder, name):
    return Video(uri=folder / name, end_action=VideoEndAction.NEXT_FILE)


def test_a_single_mode_cell_stays_single_through_the_next_file(tmp_path):
    """Next, previous and a random file, in a normal-size window.

    The shown cell keeps the whole window. The others stay hidden and
    paused, including while the old picture is let go. Empty cells of a
    fixed grid stay hidden too.
    """

    app = QApplication.instance() or QApplication([])
    folder = tmp_path / "clips"
    folder.mkdir()
    for name in ("a.mp4", "b.mp4", "c.mp4"):
        (folder / name).write_bytes(b"")

    window = QWidget()
    window.resize(1200, 700)
    ctx = _context()
    cells = []
    for number in range(6):
        cell = VideoBlock(video_driver=_Surface, context=ctx, parent=window)
        cell.setObjectName(f"v{number}")
        cell.set_video(_video(folder, "a.mp4"))
        cells.append(cell)

    _Surface.cells = cells
    _Surface.notes = []
    blocks = _Cells(cells)
    ctx.is_single_mode = False
    ctx.active_block = cells[0]
    ctx.video_blocks = blocks

    grid = GridManager(context=ctx, parent=window)
    single = SingleModeManager(context=ctx)
    ctx.is_pause_background_videos = True
    ctx.commands = SimpleNamespace(
        grid_cell_count=lambda: grid.grid_dimensions.max_size,
        remove_video_blocks=lambda *_args: None,
        set_active_block=lambda *_args: None,
        layout_order=lambda: [cell.video_id for cell in cells],
        cell_profile=lambda _video_id: None,
    )
    grid.layout_changed.connect(grid.reload_video_grid)
    single.mode_changed.connect(grid.on_single_mode_changed)
    grid.set_grid_state(
        GridState(mode=GridMode.FIXED, rows=3, cols=3, preallocate=True, is_fit=True)
    )

    shows = _Shows()
    app.installEventFilter(shows)
    try:
        window.show()
        app.processEvents()
        single.single_mode_on(cells[0])
        app.processEvents()

        assert not window.isMaximized()
        assert window.size().width() == 1200
        assert window.size().height() == 700
        assert ctx.is_single_mode
        assert cells[0].size() == window.size()

        for cell in cells[1:]:
            cell.playback_status_changed(True)
            assert cell.video_params.is_paused
            assert not cell.isVisible()

        shows.names.clear()

        steps = (
            cells[0].loop_end_action,
            lambda: cells[0].navigation.previous(is_end=True),
            lambda: cells[0].navigation.shuffle(is_end=True),
        )
        for step in steps:
            _Surface.notes.clear()
            shows.names.clear()
            step()
            app.processEvents()

            assert ctx.is_single_mode
            assert window.size().width() == 1200
            assert window.size().height() == 700
            assert not window.isMaximized()
            assert cells[0].isVisible()
            assert cells[0].size() == window.size()
            assert shows.names == []
            assert _Surface.notes

            note = _Surface.notes[-1]
            assert note["filled"]
            assert note["shown"] == (1200, 700)
            assert note["window"] == (1200, 700)
            assert note["others_visible"] == [False, False, False, False, False]
            assert True not in note["empties_visible"]

            for cell in cells[1:]:
                assert cell.video_params.is_paused
                assert not cell.isVisible()
                assert False not in cell.video_driver.asked
    finally:
        app.removeEventFilter(shows)
        for cell in cells:
            cell.navigation.close()
            cell.url_resolver.cleanup()
        window.close()
