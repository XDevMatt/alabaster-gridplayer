import logging
from pathlib import Path

from pydantic import ValidationError
from PyQt5.QtCore import QByteArray, QMimeData, QUrl

from gridplayer.models.media_list import MediaList
from gridplayer.models.video import VideoBlockMime
from gridplayer.models.video_uri import URL_ALLOWED_SCHEMES
from gridplayer.params.extensions import SUPPORTED_LIST_EXT, SUPPORTED_MEDIA_EXT
from gridplayer.utils.misc import is_remote_share, is_url

VIDEO_MIME = "application/x-gridplayer-video"

# files dropped or pasted that are taken: anything else is left out
_KNOWN_FILE_EXT = frozenset(SUPPORTED_MEDIA_EXT | SUPPORTED_LIST_EXT | {"gpls"})

# the list a dragged cell plays from, for another player to play it from too
LIST_MIME = "application/x-gridplayer-list"

# how much of what is pasted or dropped is looked at: each line of text is
# a path looked up on disk, and a page of text pasted by mistake would
# freeze the player for as long as that takes. As many as another
# instance may hand over (MAX_OPEN_ITEMS in utils/single_instance.py)
MAX_MIME_ITEMS = 1024
MAX_MIME_TEXT_CHARS = 1024 * 1024


class _CellMimeData(QMimeData):
    """A cell dragged: its video at once, and the list it plays from only
    once it is asked for. A channel list runs to a hundred megabytes and
    more as text, and a cell dragged about its own grid never needs it:
    only another player it is dropped on does."""

    def __init__(self, drag_data: VideoBlockMime, media_list: MediaList | None):
        super().__init__()

        self.setData(VIDEO_MIME, drag_data.model_dump_json().encode("utf-8"))

        self._media_list = media_list
        self._list_data: bytes | None = None

    def formats(self):
        formats = super().formats()

        if self._media_list is not None:
            formats.append(LIST_MIME)

        return formats

    def hasFormat(self, mime_type):
        if mime_type == LIST_MIME:
            return self._media_list is not None

        return super().hasFormat(mime_type)

    def retrieveData(self, mime_type, preferred_type):
        if mime_type != LIST_MIME or self._media_list is None:
            return super().retrieveData(mime_type, preferred_type)

        if self._list_data is None:
            self._list_data = self._media_list.model_dump_json().encode("utf-8")

        return QByteArray(self._list_data)


def cell_mime_data(
    drag_data: VideoBlockMime, media_list: MediaList | None
) -> QMimeData:
    return _CellMimeData(drag_data, media_list)


def mime_has_video(dnd_data: QMimeData) -> bool:
    return dnd_data.hasFormat(VIDEO_MIME)


def extract_mime_video(dnd_data: QMimeData) -> VideoBlockMime | None:
    """The cell dragged, None for none, or for one that makes no sense
    here: from a player of another version."""

    if not mime_has_video(dnd_data):
        return None

    try:
        return VideoBlockMime.model_validate_json(
            bytes(dnd_data.data(VIDEO_MIME)).decode("utf-8")
        )
    except (ValidationError, UnicodeDecodeError) as e:
        logging.getLogger(__name__).warning(f"Dragged cell left out: {e}")
        return None


def extract_mime_list(dnd_data: QMimeData) -> MediaList | None:
    """The list a cell dragged from another player plays from, None for
    none, or for one that makes no sense here."""

    if not dnd_data.hasFormat(LIST_MIME):
        return None

    try:
        return MediaList.model_validate_json(
            bytes(dnd_data.data(LIST_MIME)).decode("utf-8")
        )
    except (ValidationError, UnicodeDecodeError) as e:
        logging.getLogger(__name__).warning(f"Dragged list left out: {e}")
        return None


def extract_mime_uris(dnd_data: QMimeData) -> list[str]:
    uris = []

    if dnd_data.hasUrls():
        for url in dnd_data.urls()[:MAX_MIME_ITEMS]:
            if url.isLocalFile():
                uris.append(url.toLocalFile())
            else:
                uris.append(url.url())

    elif dnd_data.hasText():
        dnd_text = dnd_data.text()[:MAX_MIME_TEXT_CHARS].splitlines()
        uris = [line.strip() for line in dnd_text if line.strip()]
        # a link to a file as text, as a browser copies one
        uris = [_local_path_of(uri) for uri in uris[:MAX_MIME_ITEMS]]

    return _filter_uris(uris)


def _local_path_of(uri: str) -> str:
    if not uri.lower().startswith("file:"):
        return uri

    url = QUrl(uri)

    return url.toLocalFile() if url.isLocalFile() else uri


def is_allowed_url(uri: str) -> bool:
    """A link of a kind a cell plays, as the Add URLs dialog offers: not
    file:// or smb:// to another computer, nor any other program's own
    kind of link."""

    return is_url(uri) and uri.split("://", 1)[0].lower() in URL_ALLOWED_SCHEMES


def _filter_uris(uris: list[str]) -> list[str]:
    # a folder is played as the list of what is in it
    def _is_playable_file_or_folder(u: str) -> bool:
        try:
            path = Path(u)
            if path.is_dir():
                return True
            return _is_known_file_name(path.name) and path.is_file()
        except OSError:
            return False

    def _is_taken(u: str) -> bool:
        # a link Qt could not make sense of, as nothing: as a path it is
        # the folder the player runs in, all of it added
        if not u:
            return False

        if is_url(u):
            return is_allowed_url(u)

        # not even looked at: see is_remote_share
        if is_remote_share(u):
            logging.getLogger(__name__).warning(f"Left out, on another computer: {u}")
            return False

        return _is_playable_file_or_folder(u)

    return [u for u in uris if _is_taken(u)]


def _is_known_file_name(name: str) -> bool:
    """A media file, a list file or a playlist, by its extension."""

    _, dot, extension = name.rpartition(".")

    return bool(dot) and extension.lower() in _KNOWN_FILE_EXT


def get_playlist_path(uris: list[str | Path]) -> Path | None:
    for uri in uris:
        uri_path = Path(uri)
        if uri_path.suffix.lower() == ".gpls" and uri_path.is_file():
            return uri_path

    return None
