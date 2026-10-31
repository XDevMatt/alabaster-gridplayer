"""The opt-in plugins' settings (Alabaster). Nothing in gridplayer.plugins is
imported while these are off; see gridplayer.plugins."""

from gridplayer.params.settings_fields.kinds import (
    CheckboxField,
    SettingField,
)
from gridplayer.utils.qt import translate

PLUGIN_FIELDS: tuple[SettingField, ...] = (
    CheckboxField(
        settings_key="plugins/subtitlecat",
        label=translate("SettingsDialog", "Enable SubtitleCat"),
        tooltip=translate(
            "SettingsDialog",
            "Adds Find subtitles on SubtitleCat to a cell's Subtitles menu.",
        ),
    ),
    CheckboxField(
        settings_key="plugins/subtitlecat_translate",
        label=translate("SettingsDialog", "Request translations"),
        tooltip=translate(
            "SettingsDialog",
            "Lets the SubtitleCat window ask the site to translate a subtitle."
            " One request per click, never retried; the site's reply, a limit or"
            " VIP message too, is shown as sent. Needs SubtitleCat enabled.",
        ),
    ),
)
