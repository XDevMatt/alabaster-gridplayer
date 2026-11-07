"""The cell dialog: search, then languages, then one download or translate.

Opening it does not contact SubtitleCat. Each button is one request.
Sign in and Sign up only open subtitlecat.com in the default browser.
"""

import urllib.parse
from pathlib import Path

from PyQt5 import sip
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from gridplayer.plugins.subtitlecat.client import (
    DownloadOutcome,
    EmptySearch,
    NoSession,
    PageOutcome,
    PluginOff,
    SearchOutcome,
    SubtitleCatClient,
    SubtitleCatError,
    TimedOut,
    TranslateOff,
    TranslateOutcome,
)
from gridplayer.plugins.subtitlecat.names import safe_subtitle_name, search_terms
from gridplayer.plugins.subtitlecat.parse import (
    order_languages,
    preferred_language_codes,
)
from gridplayer.plugins.subtitlecat.save import SaveError, save_bytes, subtitle_folder
from gridplayer.settings import Settings
from gridplayer.utils.off_thread import OffThread
from gridplayer.utils.qt import translate


def open_subtitlecat(which: str) -> None:
    """Open the sign-in or sign-up page. Any other value is ignored."""

    if which == "sign-in":
        url = "https://www.subtitlecat.com/login.php"
    elif which == "sign-up":
        url = "https://www.subtitlecat.com/register.php"
    else:
        return

    QDesktopServices.openUrl(QUrl(url))


def terms_for_block(block) -> str:
    """Search words cleaned from the file name, or the title, or the URL."""

    params = getattr(block, "video_params", None)

    if params is None:
        return ""

    uri = getattr(params, "uri", None)

    if isinstance(uri, Path):
        return search_terms(uri.name)

    title = getattr(params, "title", None)

    if title:
        return search_terms(str(title))

    if uri:
        segment = urllib.parse.unquote(str(uri).replace("\\", "/").rsplit("/", 1)[-1])
        return search_terms(segment)

    return ""


class SubtitleCatDialog(QDialog):
    def __init__(self, block, parent=None, client=None, settings_get=None):
        super().__init__(parent)
        self._block = block
        self._client = client or SubtitleCatClient()
        self._settings_get = settings_get
        self._busy = False
        self._closed = False
        self._hits = ()
        self._languages = ()
        self._page_url = ""
        self._search_url = ""
        self._held_body = None
        self._held_name = ""
        self._download_url = ""

        self.setWindowTitle(translate("SubtitleCat", "Find subtitles on SubtitleCat.com"))
        self.resize(560, 480)
        self._build()
        self._terms.setText(terms_for_block(block))
        self._worker = OffThread(self)
        self._worker.done.connect(self._finished)

    def closeEvent(self, event):
        self._closed = True
        super().closeEvent(event)

    def _build(self) -> None:
        layout = QVBoxLayout(self)

        terms_row = QHBoxLayout()
        self._terms = QLineEdit()
        self._terms.setPlaceholderText(
            translate("SubtitleCat", "Enter a title to search for.")
        )
        self._search = QPushButton(translate("SubtitleCat", "Search"))
        self._search.clicked.connect(self._on_search)
        terms_row.addWidget(self._terms)
        terms_row.addWidget(self._search)
        layout.addLayout(terms_row)

        layout.addWidget(QLabel(translate("SubtitleCat", "Results")))
        self._results = QListWidget()
        self._results.itemDoubleClicked.connect(lambda _item: self._on_languages())
        layout.addWidget(self._results)

        self._languages_button = QPushButton(translate("SubtitleCat", "Show languages"))
        self._languages_button.clicked.connect(self._on_languages)
        layout.addWidget(self._languages_button)

        layout.addWidget(QLabel(translate("SubtitleCat", "Languages")))
        self._language_list = QListWidget()
        layout.addWidget(self._language_list)

        action_row = QHBoxLayout()
        self._download = QPushButton(translate("SubtitleCat", "Download"))
        self._translate = QPushButton(translate("SubtitleCat", "Translate"))
        self._download.clicked.connect(self._on_download)
        self._translate.clicked.connect(self._on_translate)
        action_row.addWidget(self._download)
        action_row.addWidget(self._translate)
        action_row.addStretch()
        layout.addLayout(action_row)

        self._status = QPlainTextEdit()
        self._status.setReadOnly(True)
        self._status.setMaximumHeight(120)
        layout.addWidget(self._status)

        account_row = QHBoxLayout()
        sign_up = QPushButton(translate("SubtitleCat", "Sign up"))
        sign_in = QPushButton(translate("SubtitleCat", "Sign in"))
        sign_up.clicked.connect(lambda _checked=False: open_subtitlecat("sign-up"))
        sign_in.clicked.connect(lambda _checked=False: open_subtitlecat("sign-in"))
        account_row.addWidget(sign_up)
        account_row.addWidget(sign_in)
        account_row.addStretch()
        layout.addLayout(account_row)

        self._translate.setVisible(self._translate_on())

    def _on_search(self, _checked=False) -> None:
        if self._busy:
            return

        words = self._terms.text().strip()

        if not words:
            self._status.setPlainText(
                translate("SubtitleCat", "Enter a title to search for.")
            )
            return

        self._start("search", self._client.search, words)

    def _on_languages(self, _checked=False) -> None:
        if self._busy:
            return

        row = self._results.currentRow()

        if row < 0 or row >= len(self._hits):
            self._status.setPlainText(translate("SubtitleCat", "Choose a result."))
            return

        hit = self._hits[row]
        self._page_url = hit.href
        referer = self._search_url or "https://www.subtitlecat.com/"
        self._start("page", self._client.page, hit.href, referer)

    def _on_download(self, _checked=False) -> None:
        if self._busy:
            return

        if self._held_body is not None:
            self._save_and_load(self._held_name, self._held_body)
            return

        url = self._download_url or self._selected_download()

        if not url:
            self._status.setPlainText(
                translate("SubtitleCat", "Choose a language that has a file.")
            )
            return

        referer = self._page_url or "https://www.subtitlecat.com/"
        self._start("download", self._client.download, url, referer)

    def _on_translate(self, _checked=False) -> None:
        if self._busy:
            return

        if not self._translate_on():
            self._translate.setVisible(False)
            self._status.setPlainText(
                translate(
                    "SubtitleCat",
                    "Requesting a translation is turned off in Settings.",
                )
            )
            return

        row = self._selected_language()

        if row is None or row.translate is None:
            self._status.setPlainText(
                translate("SubtitleCat", "Choose a language that is not translated.")
            )
            return

        page = self._page_url or "https://www.subtitlecat.com/"
        self._start("translate", self._client.translate, row.translate, page)

    def _start(self, what, function, *args) -> None:
        self._set_busy(True)
        self._worker.run(what, function, *args)

    def _finished(self, what, result, error) -> None:
        if self._closed or sip.isdeleted(self):
            return

        self._set_busy(False)

        if error is not None:
            self._show_error(error)
            return

        if what == "search" and isinstance(result, SearchOutcome):
            self._show_hits(result)
        elif what == "page" and isinstance(result, PageOutcome):
            self._show_languages(result)
        elif what == "download" and isinstance(result, DownloadOutcome):
            self._show_download(result)
        elif what == "translate" and isinstance(result, TranslateOutcome):
            self._show_translate(result)

    def _show_error(self, error) -> None:
        if isinstance(
            error, EmptySearch | NoSession | TimedOut | PluginOff | TranslateOff
        ):
            self._status.setPlainText(str(error))
            return

        if isinstance(error, SubtitleCatError | SaveError):
            self._status.setPlainText(str(error))
            return

        self._status.setPlainText(
            translate("SubtitleCat", "SubtitleCat.com could not be reached.")
        )

    def _show_hits(self, outcome: SearchOutcome) -> None:
        self._hits = outcome.hits
        query = urllib.parse.urlencode({"search": self._terms.text().strip()})
        self._search_url = "https://www.subtitlecat.com/index.php?" + query
        self._results.clear()
        self._languages = ()
        self._language_list.clear()
        self._download_url = ""
        self._held_body = None

        for hit in outcome.hits:
            self._results.addItem(_hit_label(hit))

        if outcome.message:
            self._status.setPlainText(outcome.message)
        elif not outcome.hits:
            self._status.setPlainText(translate("SubtitleCat", "No subtitles found."))
        else:
            found = translate("SubtitleCat", "Found {count}.")
            self._status.setPlainText(found.replace("{count}", str(len(outcome.hits))))

    def _show_languages(self, outcome: PageOutcome) -> None:
        preferred = _preferred(self._block, self._settings_get)
        self._languages = order_languages(outcome.languages, preferred)
        self._language_list.clear()
        self._download_url = ""
        self._held_body = None
        translate_on = self._translate_on()
        self._translate.setVisible(translate_on)

        for row in self._languages:
            self._language_list.addItem(_language_label(row, translate_on))

        if outcome.message:
            self._status.setPlainText(outcome.message)
        elif not self._languages:
            self._status.setPlainText(
                translate("SubtitleCat", "No languages on that page.")
            )

    def _show_download(self, outcome: DownloadOutcome) -> None:
        if outcome.kind == "subtitle":
            self._save_and_load(outcome.filename, outcome.body)
            return

        self._status.setPlainText(outcome.message)

    def _show_translate(self, outcome: TranslateOutcome) -> None:
        self._download_url = outcome.download_url or ""
        self._held_body = outcome.body
        self._held_name = outcome.filename
        text = outcome.text

        if outcome.download_url:
            ready = translate(
                "SubtitleCat",
                "A subtitle is ready. Choose Download to save it.",
            )
            text = text + "\n" + ready if text else ready

        self._status.setPlainText(text)

    def _save_and_load(self, name: str, body: bytes) -> None:
        params = getattr(self._block, "video_params", None)
        uri = getattr(params, "uri", None)

        try:
            folder = subtitle_folder(uri)
            path = save_bytes(folder, safe_subtitle_name(name), body)
        except SaveError as exc:
            self._status.setPlainText(str(exc))
            return

        subtitles = getattr(self._block, "subtitles", None)

        if subtitles is not None:
            subtitles.add_external([path.resolve()])

        saved = translate("SubtitleCat", "Saved {name}.")
        self._status.setPlainText(saved.replace("{name}", path.name))
        self._held_body = None
        self._download_url = ""

    def _selected_download(self) -> str:
        row = self._selected_language()

        if row is None or not row.download_url:
            return ""

        return row.download_url

    def _selected_language(self):
        index = self._language_list.currentRow()

        if index < 0 or index >= len(self._languages):
            return None

        return self._languages[index]

    def _translate_on(self) -> bool:
        getter = self._settings_get or _settings_get

        try:
            plugin = bool(getter("plugins/subtitlecat"))
            translate_on = bool(getter("plugins/subtitlecat_translate"))
        except (KeyError, ValueError, TypeError):
            return False

        return plugin and translate_on

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy

        for button in (
            self._search,
            self._languages_button,
            self._download,
            self._translate,
        ):
            button.setEnabled(not busy)


def _settings_get(key: str):
    return Settings().get(key)


def _preferred(block, settings_get) -> tuple[str, ...]:
    params = getattr(block, "video_params", None)
    languages = getattr(params, "subtitle_languages", "") or ""
    getter = settings_get or _settings_get

    try:
        player = getter("player/language") or ""
    except (KeyError, ValueError, TypeError):
        player = ""

    return preferred_language_codes(str(languages), str(player))


def _hit_label(hit) -> str:
    parts = []

    if hit.size:
        parts.append(hit.size)

    if hit.downloads:
        label = translate("SubtitleCat", "{count} downloads")
        parts.append(label.replace("{count}", hit.downloads))

    if hit.languages:
        label = translate("SubtitleCat", "{count} languages")
        parts.append(label.replace("{count}", hit.languages))

    if hit.source_language:
        label = translate("SubtitleCat", "from {language}")
        parts.append(label.replace("{language}", hit.source_language))

    if not parts:
        return hit.title

    return hit.title + " (" + ", ".join(parts) + ")"


def _language_label(row, translate_on: bool) -> str:
    if row.download_url:
        action = translate("SubtitleCat", "Download")
    elif row.translate is not None and translate_on:
        action = translate("SubtitleCat", "Translate")
    else:
        action = translate("SubtitleCat", "not translated")

    name = row.name or row.code
    return name + " (" + row.code + ") - " + action
