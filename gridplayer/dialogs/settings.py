import contextlib
import threading

from PyQt5.QtCore import QLocale, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gridplayer.dialogs.checkup import CheckupDialog
from gridplayer.dialogs.messagebox import QCustomMessageBox
from gridplayer.dialogs.paged_dialog import Icon, PagedDialog
from gridplayer.models.settings_draft import SettingsMode, SetValue
from gridplayer.params.settings_pages import PAGES
from gridplayer.params.static import CacheMode
from gridplayer.params.theme import set_secondary
from gridplayer.playlist_settings import PlaylistSettings
from gridplayer.settings import Settings, default_value
from gridplayer.utils import cache
from gridplayer.utils.app_dir import get_app_data_dir
from gridplayer.utils.network import opts_for
from gridplayer.utils.qt import translate
from gridplayer.utils.screenshots import unknown_specifiers
from gridplayer.utils.show_in_folder import open_folder
from gridplayer.utils.ytdlp_provenance import external_binary
from gridplayer.widgets.settings_controls import icon_button
from gridplayer.widgets.settings_form import SettingsForm

# the only pages the SubtitleCat buttons open (Alabaster has no account)
SUBTITLECAT_SIGN_UP_URL = "https://www.subtitlecat.com/register.php"
SUBTITLECAT_SIGN_IN_URL = "https://www.subtitlecat.com/login.php"
SUBTITLECAT_URLS = frozenset((SUBTITLECAT_SIGN_UP_URL, SUBTITLECAT_SIGN_IN_URL))

# beside the label of a setting the open playlist has its own value for
MARK_ICON_PX = 16


def _on_the_right(*widgets):
    """Widgets on a line, on the right of it."""

    row = QWidget()

    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch(1)
    for widget in widgets:
        layout.addWidget(widget)

    return row


class SettingsDialog(PagedDialog):
    """The pages of gridplayer.params.settings_pages, each one a SettingsForm.

    What is here is what a page can't say for itself: the buttons and lists
    that aren't settings (the Slots), and the few settings that lean on each
    other in a way a rule can't put.
    """

    # what the cache comes to, worked out on a thread of its own
    cache_measured = pyqtSignal(object)

    def __init__(self, parent, page: str | None = None):
        """page: the id of the page to open on (Alabaster: the Shortcuts
        command opens on "shortcuts"); the first page by default."""

        super().__init__(parent)

        self.ui_build()
        self.ui_connect()

        self.load_settings()

        # after the values are in, so a setting saved on warns of nothing
        self.ui_connect_warnings()

        self.measure_cache()
        self.switch_page(None)
        self._open_named_page(page)
        self.fit_to_screen()

    def _open_named_page(self, page: str | None):
        if page is None:
            return

        if page not in self.pages:
            raise ValueError(f"no settings page named {page}")

        self.show_page(page)

    # building

    def ui_build(self):
        self.setWindowTitle(translate("SettingsDialog", "Settings"))

        body = self.build_index(search=True)

        self.dataDirOpen = QPushButton(
            QIcon.fromTheme("show-in-folder"),
            translate("SettingsDialog", "Open data folder"),
        )
        self.dataDirOpen.setMinimumWidth(130)
        self.dataDirOpen.setToolTip(
            translate(
                "SettingsDialog",
                "Holds the log and settings. You can also put a JavaScript"
                " runtime here.",
            )
        )

        buttons = QHBoxLayout()
        buttons.addWidget(self.dataDirOpen)
        buttons.addWidget(self.buttonBox, 1)

        root = QVBoxLayout(self)
        root.addLayout(body, 1)
        root.addLayout(buttons)

        # the pages last, built where they go: a widget moved under another
        # parent is styled over again, all of it, and the pages are most of
        # what the dialog has
        self._build_index()

    def _build_index(self):
        slots = self._slots()

        for group in PAGES:
            self.add_heading(group.title)

            for page in group.pages:
                form = SettingsForm(
                    page.items,
                    reset_to=default_value,
                    mode=SettingsMode.DEFAULTS,
                    slots=slots,
                )
                self.add_form_page(page, form, self._mark_playlist_own(form))

    def _mark_playlist_own(self, form: SettingsForm) -> str | None:
        """The settings the open playlist has its own value for, which a
        change here won't reach: marked on their rows, and said at the top
        of the page, as what it says."""

        session = PlaylistSettings()

        own = [key for key in form.keys() if session.is_overridden(key)]

        if not own:
            return None

        # every row marked would say nothing
        if len(own) == len(form.keys()):
            return translate(
                "SettingsDialog",
                "The open playlist keeps all its settings. A change here won't"
                " reach it.",
            )

        for key in own:
            form.add_mark(key, self._own_value_mark(form, key, session.get(key)))

        return translate(
            "SettingsDialog",
            "The open playlist has its own value for the settings marked with the"
            " playlist icon. A change here won't reach it.",
        )

    @staticmethod
    def _own_value_mark(form: SettingsForm, key: str, value) -> QWidget:
        mark = Icon("page-playlist", MARK_ICON_PX)

        text = form.text_of(key, value)
        if text is None:
            mark.setToolTip(
                translate("SettingsDialog", "The open playlist has its own value.")
            )
        else:
            mark.setToolTip(
                translate(
                    "SettingsDialog", "The open playlist has its own value: {VALUE}"
                ).format(VALUE=text)
            )

        return mark

    def _slots(self):
        """What fills each Slot of the pages: _slot_<name>."""

        return {
            name.removeprefix("_slot_"): getattr(self, name)
            for name in dir(type(self))
            if name.startswith("_slot_")
        }

    def _slot_cache_clear(self):
        self.cacheSize = QLabel()
        set_secondary(self.cacheSize)

        self.cacheClear = QPushButton(
            QIcon.fromTheme("trash"), translate("SettingsDialog", "Clear")
        )
        self.cacheClear.setToolTip(
            translate(
                "SettingsDialog", "Delete everything in the cache folder:\n{FOLDER}"
            ).format(FOLDER=cache.cache_root())
        )
        self.cacheClear.clicked.connect(self.clear_cache)

        # the folder it is in, as a folder field's button
        self.cacheOpen = icon_button(
            "show-in-folder", translate("SettingsDialog", "Open Folder")
        )
        self.cacheOpen.clicked.connect(self.open_cache_dir)

        row = _on_the_right(self.cacheSize, self.cacheClear, self.cacheOpen)
        # as far apart as fields in a row are
        row.layout().setSpacing(8)
        return row

    def _slot_screenshot_template_help(self):
        self.screenshotsFilenameTemplateHelpButton = icon_button(
            "question", translate("SettingsDialog", "Screenshot file name format")
        )
        self.screenshotsFilenameTemplateHelpButton.clicked.connect(
            self.show_screenshot_template_help
        )
        return self.screenshotsFilenameTemplateHelpButton

    def _slot_youtube_test(self):
        self.streamingTestButton = QPushButton(
            QIcon.fromTheme("checkup"),
            translate("SettingsDialog", "Test a YouTube link"),
        )
        self.streamingTestButton.setToolTip(
            translate(
                "SettingsDialog",
                "Open a YouTube link step by step and show which step fails",
            )
        )
        self.streamingTestButton.clicked.connect(self.run_youtube_checkup)
        return _on_the_right(self.streamingTestButton)

    def _slot_subtitlecat_account(self):
        """Sign up and Sign in, each opening that one page in the browser."""

        self.subtitleCatSignUp = QPushButton(translate("SettingsDialog", "Sign up"))
        self.subtitleCatSignUp.setToolTip(SUBTITLECAT_SIGN_UP_URL)
        self.subtitleCatSignUp.clicked.connect(self.open_subtitlecat_sign_up)

        self.subtitleCatSignIn = QPushButton(translate("SettingsDialog", "Sign in"))
        self.subtitleCatSignIn.setToolTip(SUBTITLECAT_SIGN_IN_URL)
        self.subtitleCatSignIn.clicked.connect(self.open_subtitlecat_sign_in)

        row = _on_the_right(self.subtitleCatSignUp, self.subtitleCatSignIn)
        row.layout().setSpacing(8)
        return row

    def _slot_network_test(self):
        self.networkTestButton = QPushButton(
            QIcon.fromTheme("checkup"), translate("SettingsDialog", "Test network")
        )
        self.networkTestButton.setToolTip(
            translate(
                "SettingsDialog",
                "Test these settings on a real link and show which step fails",
            )
        )
        self.networkTestButton.clicked.connect(self.run_network_checkup)
        return _on_the_right(self.networkTestButton)

    def ui_connect(self):
        self.connect_pages()

        self.dataDirOpen.clicked.connect(self.open_data_dir)

        self.cache_measured.connect(self.show_cache_size)

        self.form_of("cache/mode").values_changed.connect(self.cache_mode_selected)

    def ui_connect_warnings(self):
        """PATH engines and an external yt-dlp binary (Alabaster security):
        off by default, and warned of as they are turned on."""

        self.widget("streaming/js_runtime_allow_path").toggled.connect(
            self._warn_if_path_engines
        )
        self.widget("streaming/ytdlp_external_path").editingFinished.connect(
            self._warn_if_external_ytdlp
        )

    @staticmethod
    def _path_impersonation_warning() -> str:
        return translate(
            "SettingsDialog",
            "A program on PATH can be replaced by another file of the same"
            " name. GridPlayer will then run that file. Only enable this if"
            " you installed the binary yourself and trust this machine.",
        )

    def _warn_if_path_engines(self, checked: bool):
        if not checked:
            return

        QCustomMessageBox.warning(
            self,
            translate("SettingsDialog", "Allow engines on PATH"),
            self._path_impersonation_warning(),
        )

    def _warn_if_external_ytdlp(self):
        configured = self.value("streaming/ytdlp_external_path").strip()
        if not configured:
            return

        found = external_binary(configured)

        if found is None:
            text = translate(
                "SettingsDialog",
                "No yt-dlp program was found at {PATH} or on PATH. Links will be"
                " resolved with the built-in yt-dlp module until it is.",
            ).replace("{PATH}", configured)
        else:
            text = " ".join(
                (
                    translate(
                        "SettingsDialog",
                        "Links will be resolved by running {PATH}. Keep it updated"
                        " yourself (for example yt-dlp -U, winget upgrade or brew"
                        " upgrade).",
                    ).replace("{PATH}", str(found)),
                    self._path_impersonation_warning(),
                )
            )

        QCustomMessageBox.warning(
            self, translate("SettingsDialog", "External yt-dlp"), text
        )

    # settings that lean on each other

    def cache_mode_selected(self, *_):
        # nothing on disk to see, kept in memory
        self.cacheOpen.setEnabled(self.value("cache/mode") == CacheMode.DISK)

    # loading and saving

    def load_settings(self):
        for form in self.forms.values():
            form.set_values({key: Settings().get(key) for key in form.keys()})

        self.cache_mode_selected()
        self.update_reset_page()

    def save_settings(self):
        for form in self.forms.values():
            for key, change in form.persistence_result().items():
                if isinstance(change, SetValue):
                    Settings().set(key, change.value)
                else:
                    Settings().reset(key)

    def is_screenshot_template_valid(self):
        template = self.widget("screenshots/filename_template")

        unknown = unknown_specifiers(template.text())

        if not unknown:
            return True

        QCustomMessageBox.warning(
            self,
            translate("SettingsDialog", "Screenshots"),
            translate(
                "SettingsDialog", "Unknown specifiers in the file name: {SPECIFIERS}"
            ).format(SPECIFIERS=", ".join(unknown)),
            info=translate("SettingsDialog", "Write %% for a percent sign."),
        )

        self.show_page_of("screenshots/filename_template")
        self.form_of("screenshots/filename_template").point_to(
            "screenshots/filename_template"
        )

        return False

    def accept(self):
        if not self.is_screenshot_template_valid():
            return

        self.save_settings()

        super().accept()

    # what the buttons do

    def run_youtube_checkup(self):
        """Resolve a real link the way playback would, step by step.

        It lives on this page rather than beside the cookies because
        two of its six steps are about cookies and the other four are
        about whether a link resolves at all, which is what this page
        is for. The runtime it can report as missing is set here too.

        Every setting it uses is read off the pages rather than out of
        the store: the point is to try what is on screen, which may be
        a runtime folder just typed, a proxy just changed, or an import
        of cookies nobody has pressed OK on yet.
        """

        # yt-dlp and streamlink are slow to import, and the settings dialog
        # is imported at startup
        from gridplayer.utils.ytdlp_checkup import YouTubeCheckup

        # no stored jar (Alabaster): the browser on the Cookies page, if any
        checkup = YouTubeCheckup(
            jar=None,
            are_cookies_enabled=False,
            js_runtime_path=self.value("streaming/js_runtime_path"),
            net_opts=self.network_opts_on_page,
            browser=self.value("cookies/from_browser") or "",
            browser_profile=self.value("cookies/browser_profile"),
        )

        CheckupDialog(self, checkup).exec_()

    def run_network_checkup(self):
        """Try the network settings as the page has them now.

        Read off the widgets rather than out of the store, for the same
        reason the cookies test is: what somebody wants tried is what
        they have just typed, and they have not pressed OK yet.
        """

        # slow to import for the same reason as the YouTube one
        from gridplayer.utils.network_checkup import NetworkCheckup

        CheckupDialog(self, NetworkCheckup(self.network_opts_on_page)).exec_()

    @property
    def network_opts_on_page(self):
        """The Network page as the settings it would be saved as."""

        return opts_for(
            proxy_mode=self.value("network/proxy_mode"),
            proxy_url=self.value("network/proxy_url"),
            user_agent=self.value("network/user_agent"),
            force_ipv4=self.value("network/force_ipv4"),
            timeout=self.value("network/timeout"),
            verify_tls=self.value("network/verify_tls"),
        )

    def show_screenshot_template_help(self):
        """The specifiers, in a box of their own.

        Seven of them with what each gives is a table, and a table does not
        go in a tooltip anyone can read or under a field on a page that is
        already full. See gridplayer.utils.screenshots for what they do.
        """

        help_text = translate(
            "SettingsDialog",
            "<p>The file name is made from the format, with these replaced:</p>"
            "<table cellspacing='0' cellpadding='3'>"
            "<tr><td><tt>%f</tt></td><td>video name</td></tr>"
            "<tr><td><tt>%F</tt></td><td>video name without extension</td></tr>"
            "<tr><td><tt>%p</tt></td><td>position in the video, 01-02-03</td></tr>"
            "<tr><td><tt>%P</tt></td>"
            "<td>position in the video with milliseconds, 01-02-03.456</td></tr>"
            "<tr><td><tt>%n</tt></td>"
            "<td>number, 0001 and up, the first one not taken yet</td></tr>"
            "<tr><td><tt>%D</tt></td><td>date, 2026-09-24</td></tr>"
            "<tr><td><tt>%T</tt></td>"
            "<td>date and time, 2026-09-24_13-05-09</td></tr>"
            "<tr><td><tt>%tY</tt></td><td>year, 2026</td></tr>"
            "<tr><td><tt>%ty</tt></td><td>year, 26</td></tr>"
            "<tr><td><tt>%tm</tt></td><td>month, 09</td></tr>"
            "<tr><td><tt>%td</tt></td><td>day, 24</td></tr>"
            "<tr><td><tt>%tH</tt></td><td>hour, 13</td></tr>"
            "<tr><td><tt>%tM</tt></td><td>minute, 05</td></tr>"
            "<tr><td><tt>%tS</tt></td><td>second, 09</td></tr>"
            "<tr><td><tt>%%</tt></td><td>a percent sign</td></tr>"
            "</table>"
            "<p>For example:</p>"
            "<table cellspacing='0' cellpadding='3'>"
            "<tr><td><tt>%F_%P</tt></td><td><tt>clip_00-01-02.345.png</tt></td></tr>"
            "<tr><td><tt>%D_%n</tt></td>"
            "<td><tt>2026-09-24_0001.png</tt></td></tr>"
            "<tr><td><tt>%F %T</tt></td>"
            "<td><tt>clip 2026-09-24_13-05-09.png</tt></td></tr>"
            "</table>"
            "<p>Without <tt>%n</tt>, a name that is taken gets a number"
            " in brackets after it. Characters a file name can't have are"
            " replaced with <tt>_</tt>. Leave the format empty to go back to"
            " <tt>%F_%P</tt>.</p>",
        )

        QCustomMessageBox.information(
            self,
            translate("SettingsDialog", "Screenshots"),
            translate("SettingsDialog", "Screenshot file name format"),
            info=help_text,
        )

    # SubtitleCat (Alabaster)

    def open_subtitlecat_sign_up(self, _checked=False):
        """The sign-up page, and nothing else. Alabaster has no account."""

        self._open_subtitlecat_page(SUBTITLECAT_SIGN_UP_URL)

    def open_subtitlecat_sign_in(self, _checked=False):
        """The sign-in page, and nothing else."""

        self._open_subtitlecat_page(SUBTITLECAT_SIGN_IN_URL)

    @staticmethod
    def _open_subtitlecat_page(url: str) -> None:
        # The two buttons are the only callers. Anything else is refused,
        # so a click cannot be pointed at some other address.
        if url not in SUBTITLECAT_URLS:
            return

        QDesktopServices.openUrl(QUrl(url))

    # folders and the cache

    def open_cache_dir(self):
        folder = cache.cache_root()

        # opened before anything was kept there, as an empty folder
        folder.mkdir(parents=True, exist_ok=True)

        open_folder(folder)

    def open_data_dir(self):
        """The folder rather than the log file that used to be opened.

        The log is in there and named for what it is, so nothing is lost
        by stopping one short of it, and the folder is now somewhere a
        person is sent for reasons of their own: it is where a
        JavaScript runtime goes on the packages that cannot see one
        installed anywhere else. See gridplayer.utils.js_runtime.
        """

        open_folder(get_app_data_dir())

    def measure_cache(self, first=None):
        """What the cache comes to, put beside Clear once it is known.

        On a thread of its own, after whatever is to be done first: a
        large cache is a lot of files to look over, or to delete.
        """

        def work():
            if first is not None:
                first()

            size = cache.kept_bytes()

            # the dialog may have gone meanwhile
            with contextlib.suppress(RuntimeError):
                self.cache_measured.emit(size)

        threading.Thread(target=work, name="cache size", daemon=True).start()

    def clear_cache(self):
        """Cleared at once rather than on OK: nothing is lost but what
        would be downloaded again."""

        self.cacheClear.setEnabled(False)
        self.cacheSize.setText(translate("SettingsDialog", "Clearing..."))

        self.measure_cache(first=cache.clear)

    def show_cache_size(self, size):
        self.cacheClear.setEnabled(size > 0)

        if size == 0:
            self.cacheSize.setText(translate("SettingsDialog", "Nothing"))
            return

        megabytes = QLocale().toString(max(size / cache.MB, 0.1), "f", 1)

        self.cacheSize.setText(
            translate("SettingsDialog", "{SIZE} MB").format(SIZE=megabytes)
        )
