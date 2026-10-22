"""SubtitleCat's settings page. Buttons open two pages and save nothing."""

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs.settings import SettingsDialog
from gridplayer.widgets.settings_page_scroll_area import PageScrollArea


def test_the_page_is_wired_and_does_not_save(monkeypatch):
    opened = []
    monkeypatch.setattr(
        "gridplayer.dialogs.settings.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()),
    )
    dialog = SettingsDialog(None)

    try:
        assert dialog.settings_map["plugins/subtitlecat"] is dialog.pluginsSubtitleCat
        assert (
            dialog.settings_map["plugins/subtitlecat_translate"]
            is dialog.pluginsSubtitleCatTranslate
        )
        assert isinstance(dialog.page_plugins_subtitlecat, PageScrollArea)
        assert dialog.pluginsSubtitleCat.isChecked() is False
        assert dialog.pluginsSubtitleCatTranslate.isChecked() is False

        dialog.pluginsSubtitleCat.setChecked(False)
        assert dialog.pluginsSubtitleCatTranslate.isEnabled() is True

        dialog.subtitleCatSignIn.click()
        dialog.subtitleCatSignUp.click()
        dialog._open_subtitlecat_page("https://evil.example/phish")

        assert opened == [
            "https://www.subtitlecat.com/login.php",
            "https://www.subtitlecat.com/register.php",
        ]
    finally:
        dialog.close()
        dialog.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
