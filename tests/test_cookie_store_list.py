"""Import/export of a stored jar is gone from the cookies page."""

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication

from gridplayer.dialogs.settings import SettingsDialog


def test_the_settings_page_has_no_jar_widget():
    dialog = SettingsDialog(None)
    try:
        assert not hasattr(dialog, "cookiesList")
        assert not hasattr(dialog, "cookiesEnabled")
        assert not hasattr(dialog, "cookiesAllowUpdate")
    finally:
        dialog.close()
        dialog.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_no_stored_jar_setting_is_left():
    from gridplayer.params.settings_fields.registry import FIELDS

    assert "cookies/enabled" not in FIELDS
    assert "cookies/allow_update" not in FIELDS
