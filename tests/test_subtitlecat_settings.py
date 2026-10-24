"""SubtitleCat's settings page, on upstream's settings pages. Buttons open
two pages and save nothing."""

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs.settings import SettingsDialog
from gridplayer.params.settings_pages import PAGES
from gridplayer.widgets.settings_page_scroll_area import PageScrollArea


def _plugins_group():
    (group,) = [group for group in PAGES if group.title == "Plugins"]
    return group


def test_the_plugins_heading_has_the_subtitlecat_page():
    assert [page.id for page in _plugins_group().pages] == ["subtitlecat"]
    assert _plugins_group().pages[0].title == "SubtitleCat"


def test_the_page_is_wired_and_does_not_save(monkeypatch):
    opened = []
    monkeypatch.setattr(
        "gridplayer.dialogs.settings.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()),
    )
    dialog = SettingsDialog(None)

    try:
        page = dialog.pages["subtitlecat"]
        enable = dialog.widget("plugins/subtitlecat")
        translate = dialog.widget("plugins/subtitlecat_translate")

        assert page.findChild(PageScrollArea) is not None
        assert page.isAncestorOf(enable)
        assert page.isAncestorOf(translate)
        assert page.isAncestorOf(dialog.subtitleCatSignUp)
        assert page.isAncestorOf(dialog.subtitleCatSignIn)
        assert "no SubtitleCat account" in dialog.notes["subtitlecat"].text()

        assert enable.isChecked() is False
        assert translate.isChecked() is False

        enable.setChecked(False)
        assert translate.isEnabled() is True

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


def test_enabling_it_is_saved(monkeypatch):
    from gridplayer.settings import Settings

    dialog = SettingsDialog(None)

    try:
        dialog.widget("plugins/subtitlecat").setChecked(True)
        dialog.save_settings()

        assert Settings().get("plugins/subtitlecat") is True
        assert Settings().get("plugins/subtitlecat_translate") is False
    finally:
        Settings().reset("plugins/subtitlecat")
        dialog.close()
        dialog.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
