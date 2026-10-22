"""Cookies page: request-time browser cookies only, no stored jar."""

import pytest
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs.settings import SettingsDialog


@pytest.fixture
def dialog():
    made = SettingsDialog(None)
    yield made
    made.close()
    made.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_browser_controls_are_wired(dialog):
    assert dialog.settings_map["cookies/from_browser"] is dialog.cookiesFromBrowser
    assert (
        dialog.settings_map["cookies/browser_profile"] is dialog.cookiesBrowserProfile
    )
    assert "cookies/enabled" not in dialog.settings_map
    assert "cookies/allow_update" not in dialog.settings_map
    assert not hasattr(dialog, "cookiesList")


def test_off_and_firefox_are_choices(dialog):
    assert dialog.cookiesFromBrowser.findData("") == 0
    assert dialog.cookiesFromBrowser.findData("firefox") > 0
    assert dialog.cookiesBrowserProfile.placeholderText()


def test_the_section_opens_the_cookies_page(dialog):
    entry = dialog.section_index.findItems("Cookies", Qt.MatchExactly)[0]
    dialog.section_index.setCurrentItem(entry)

    assert dialog.section_page.currentWidget() is dialog.page_streaming_cookies
