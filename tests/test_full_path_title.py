"""Show full path in the cell title: local files, cut in the middle."""

from unittest.mock import MagicMock

import pytest
from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from gridplayer.models.stream import Streams
from gridplayer.models.video import Video
from gridplayer.params.settings_fields.kinds import CheckboxField
from gridplayer.params.settings_fields.registry import FIELDS
from gridplayer.params.settings_pages import PLAYLIST_PAGE
from gridplayer.params.static import VideoInitialState
from gridplayer.player.managers.lists import MediaListsRegistry
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.settings import _default_settings
from gridplayer.utils.url_resolve.static import ResolvedVideo
from gridplayer.widgets.tooltip import _target_of
from gridplayer.widgets.video_block import VideoBlock
from gridplayer.widgets.video_frame_dummy import VideoFrameDummy
from gridplayer.widgets.video_overlay_elements import OverlayLabel

_KEY = "playlist/show_full_path_title"


@pytest.fixture(scope="module", autouse=True)
def _qapp():
    return QApplication.instance() or QApplication([])


def _context():
    context = MagicMock()
    context.is_overlay_hide_on_timeout = False
    context.is_drag_ui = False
    context.is_disable_overlay = False
    context.is_show_overlay_border = False
    context.overlay_timeout = 1
    context.synced_view = None
    context.lists = MediaListsRegistry()

    return context


@pytest.fixture
def block():
    """A stopped cell, so the title is set without opening the file."""

    window = QWidget()
    window.resize(220, 160)
    cell = VideoBlock(video_driver=VideoFrameDummy, context=_context(), parent=window)
    cell.resize(220, 160)
    window.show()
    cell.show()

    try:
        yield cell
    finally:
        PlaylistSettings().reset(_KEY)
        cell.url_resolver.cleanup()
        cell.cleanup()
        window.close()


def _file(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def _video(uri, **kwargs):
    return Video(uri=uri, playback_state=VideoInitialState.STOPPED, **kwargs)


def _move(widget, global_pos):
    local = widget.mapFromGlobal(global_pos)
    return QMouseEvent(
        QEvent.MouseMove,
        QPointF(local),
        QPointF(global_pos),
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier,
    )


def _tip_from(widget, pos):
    """What the tooltip look-up would say, starting at widget and walking up."""

    while widget is not None:
        target = _target_of(widget, pos)
        if target is not None:
            return target.text
        if widget.isWindow():
            return None
        widget = widget.parentWidget()

    return None


def test_the_setting_is_off_and_next_to_the_overlay():
    """Off unless asked, on the Overlay page beside the other title chrome."""

    assert _default_settings[_KEY] is False

    spec = FIELDS[_KEY]
    assert isinstance(spec, CheckboxField)
    assert spec.label == "Show full path in cell title"
    assert "whole path" in spec.tooltip
    assert "tooltip" in spec.tooltip

    overlay = next(section for section in PLAYLIST_PAGE if section.title == "Overlay")
    keys = [item for item in overlay.items if isinstance(item, str)]
    assert keys.index(_KEY) == keys.index("playlist/show_overlay_border") + 1


def test_uri_name_stays_the_file_name(tmp_path):
    """Lists, screenshots and bookmarks still use the file name."""

    path = _file(tmp_path / "clip.mp4")
    video = Video(uri=path)

    assert video.uri_name == "clip.mp4"
    assert video.cell_title(full_path=False) == "clip.mp4"
    assert video.cell_title(full_path=True) == str(path)

    link = Video(uri="https://example.com/watch?v=1")
    assert link.cell_title(full_path=True) == "https://example.com/watch?v=1"
    assert link.uri_name == link.cell_title(full_path=True)


def test_a_narrow_title_is_cut_in_the_middle():
    """What does not fit keeps its start and its end, and the whole text."""

    label = OverlayLabel()
    path = "C:\\videos\\" + ("holiday-folder\\" * 12) + "clip.mp4"
    label.label = path
    label.resize(220, 28)

    shown = label.printable_label(label.width(), label.font())

    assert shown != path
    assert "\u2026" in shown
    assert shown.startswith("C:")
    assert shown.endswith(".mp4")
    assert label.toolTip() == path
    # the title lets the mouse through, so a click on it still reaches the cell
    assert label.testAttribute(Qt.WA_TransparentForMouseEvents)


def test_a_local_file_uses_its_name_until_the_setting_is_on(block, tmp_path):
    path = _file(tmp_path / "holiday" / "clip.mp4")
    PlaylistSettings().reset(_KEY)

    block.set_video(_video(path))

    assert block.title == "clip.mp4"
    assert block.video_params.uri_name == "clip.mp4"

    block.apply_full_path_title(True)

    assert block.title == str(path)
    assert block._default_title == str(path)

    block.apply_full_path_title(False)

    assert block.title == "clip.mp4"


def test_a_name_the_viewer_gave_it_stays(block, tmp_path):
    path = _file(tmp_path / "clip.mp4")
    block.set_video(_video(path, title="My clip"))

    block.apply_full_path_title(True)

    assert block.title == "My clip"
    assert block._default_title == str(path)


def test_a_link_keeps_its_own_name_and_the_pages_title(block):
    """A URL is not a path, and the title the page gives it replaces that."""

    block.set_video(_video("https://example.com/watch?v=1"))
    block.apply_full_path_title(True)

    assert block.title == "https://example.com/watch?v=1"

    block.stream.load_quality = lambda *_args, **_kwargs: None
    block.set_video_url(
        ResolvedVideo(title="A page title", is_live=False, streams=Streams())
    )
    block.apply_full_path_title(True)

    assert block.title == "A page title"
    assert block._default_title == "A page title"


def test_the_whole_path_is_the_tooltip_while_the_pointer_is_on_the_title(
    block, tmp_path
):
    path = _file(tmp_path / "holiday" / "clip.mp4")
    PlaylistSettings().set(_KEY, True)
    block.set_video(_video(path))
    QApplication.processEvents()
    block.layout().activate()
    block.overlay.layout().activate()

    label = block.overlay.label_text
    assert label.label == str(path)
    assert label.width() > 0

    on_title = label.mapToGlobal(label.rect().center())
    block.mouseMoveEvent(_move(block, on_title))

    assert block.toolTip() == str(path)
    assert _tip_from(block.overlay.control_widget, on_title) == str(path)

    shown = label.printable_label(label.width(), label.font())
    assert shown != str(path)
    assert "\u2026" in shown
    assert shown.startswith(str(path)[:2])
    assert shown.endswith("mp4")

    off_title = block.mapToGlobal(QPoint(block.width() // 2, block.height() - 8))
    assert not label.rect().contains(label.mapFromGlobal(off_title))
    block.mouseMoveEvent(_move(block, off_title))

    assert block.toolTip() == ""
    assert _tip_from(block.overlay.control_widget, off_title) is None
