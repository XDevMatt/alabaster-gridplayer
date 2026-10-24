"""Cookies page: request-time browser cookies only, no stored jar
(Alabaster), on upstream's settings pages."""

import pytest
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs.settings import SettingsDialog
from gridplayer.params.settings_fields import choices


@pytest.fixture
def dialog():
    made = SettingsDialog(None)
    yield made
    made.close()
    made.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_browser_controls_are_on_the_cookies_page(dialog):
    page = dialog.pages["cookies"]

    assert page.isAncestorOf(dialog.widget("cookies/from_browser"))
    assert page.isAncestorOf(dialog.widget("cookies/browser_profile"))
    assert set(dialog.forms["cookies"].keys()) == {
        "cookies/from_browser",
        "cookies/browser_profile",
    }
    assert not hasattr(dialog, "cookiesList")


def test_off_and_firefox_are_choices(dialog):
    browser = dialog.widget("cookies/from_browser")

    assert browser.findData("") == 0
    assert browser.findData("firefox") > 0
    assert dialog.widget("cookies/browser_profile").placeholderText()


def test_off_by_default(dialog):
    assert dialog.value("cookies/from_browser") == ""
    assert dialog.value("cookies/browser_profile") == ""


def test_a_browser_yt_dlp_no_longer_knows_is_shown_as_off():
    assert choices.known_cookie_browser("netscape-navigator") == ""
    assert choices.known_cookie_browser("firefox") == "firefox"


def test_the_section_opens_the_cookies_page(dialog):
    dialog.show_page("cookies")

    assert dialog.section_page.currentWidget() is dialog.pages["cookies"]


def test_the_youtube_test_uses_the_browser_on_the_page(dialog, mocker):
    from gridplayer.dialogs import settings as settings_dialog
    from gridplayer.utils import ytdlp_checkup

    made = mocker.patch.object(ytdlp_checkup, "YouTubeCheckup")
    mocker.patch.object(settings_dialog, "CheckupDialog")

    browser = dialog.widget("cookies/from_browser")
    browser.setCurrentIndex(browser.findData("firefox"))
    dialog.widget("cookies/browser_profile").setText("default-release")

    dialog.run_youtube_checkup()

    kwargs = made.call_args.kwargs
    assert kwargs["jar"] is None
    assert kwargs["are_cookies_enabled"] is False
    assert kwargs["browser"] == "firefox"
    assert kwargs["browser_profile"] == "default-release"
