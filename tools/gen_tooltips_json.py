"""Generate docs/tooltips.json and docs/reference/settings.md from the code.

Every field of the Settings dialog, in the order the dialog shows them, with
its label, tooltip, default, range or choices, from
gridplayer/params/settings_pages.py and gridplayer/params/settings_fields.
The fields are imported, so PyQt has to be importable; no window is shown:

    QT_QPA_PLATFORM=offscreen uv run --frozen python tools/gen_tooltips_json.py

Labels and tooltips are the untranslated English ones. Where the app works
something out on the user's system (the data folder, whether there is a
tray, whether hardware video can run), the value written is the one for a
system where everything is available, and NOTES says what differs.

Only generated_at changes from one run to the next on the same code.
"""

import importlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "docs" / "tooltips.json"
MD_TARGET = ROOT / "docs" / "reference" / "settings.md"

# settings added on the 0.2beta branch are the ones master at this commit
# did not know
BASE_COMMIT = "29e02b6"
SINCE_BRANCH = "0.2beta"

PLATFORMS = ("windows", "linux", "macos")

# doc-only remarks the code can't give in a few words
NOTES = {
    "player/stay_on_top": "Not offered on Linux, where the window manager decides.",
    "player/tray_icon": "Greyed out, with the reason under it, where the desktop"
    " has no tray.",
    "player/hide_taskbar": "Greyed out on Wayland, and on GNOME, where it stops"
    " the window from minimizing.",
    "player/language": "The default is the system language when there is a"
    " translation for it, otherwise en_US. Takes effect after a restart.",
    "player/keymap": "Stored as the changes from the default keymap. The"
    " defaults are listed in the Hotkeys reference.",
    "player/video_driver": "On macOS the default is Hardware SP and Hardware is"
    " not offered. Where hardware video can't run (Wayland without Xwayland),"
    " the Software twin is used and the reason is added to the tooltip.",
    "internal/opaque_hw_overlay": "Greyed out where hardware video can't run.",
    "internal/fake_overlay_invisibility": "Greyed out where hardware video can't run.",
    "internal/hw_crop_border_offset": "Greyed out where hardware video can't run.",
    "logging/log_limit_size": "Takes effect after a restart.",
    "logging/log_limit_backups": "Takes effect after a restart.",
    "screenshots/dir": "Empty means the screenshots folder in the data folder.",
    "streaming/ytdlp_external_path": "Used for resolving links; the checkups and"
    " cookie-browser list still use the built-in module.",
    "streaming/resolver_priority_patterns": "A table of URL patterns (wildcard"
    " host, wildcard URL or regex) and the resolver each one picks.",
    "misc/vlc_options": "Written as on the VLC command line, for example"
    " --network-caching=1000.",
    "subtitles/font": "The choices are the fonts installed on the computer.",
    "video_defaults/crop": "Left, top, right and bottom margins in pixels, used"
    " when Crop is set to Margins.",
    "cookies/from_browser": "The choices are the browsers this yt-dlp can read"
    " cookies from.",
}

# said of a whole page, besides the note the page has of its own
PAGE_NOTES = {
    "playlist": "Also the first page of the Playlist window, where the values"
    " are the open playlist's own.",
    "video": "Also a page of the Playlist window, where the values are the open"
    " playlist's own. Changes apply to videos opened afterwards.",
}


def _offscreen():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(ROOT))

    from PyQt5.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _plain(text):
    """A heading or note without its HTML, and a heading without the
    [reference] link after it."""

    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()

    return re.sub(r"\s*\[[^\]]*\]$", "", text)


def _jsonable(value):
    from pydantic import BaseModel

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _walk(items, heading, out):
    """(key or field, heading) for each setting on a page, in order."""

    from gridplayer.params.settings_fields.kinds import (
        Indented,
        Note,
        Row,
        Section,
        SettingField,
        Slot,
    )

    for item in items:
        if isinstance(item, str | SettingField):
            out.append((item, heading))
        elif isinstance(item, Section):
            _walk(item.items, _plain(item.title), out)
        elif isinstance(item, Row | Indented):
            _walk(item.items, heading, out)
        elif isinstance(item, Note | Slot):
            continue
        else:
            raise SystemExit(f"unknown layout item {item!r}")

    return out


def _type_of(spec):
    from gridplayer.params.settings_fields import kinds

    order = (
        (kinds.CheckboxField, "bool"),
        (kinds.SpinField, "int"),
        (kinds.FloatSpinField, "float"),
        (kinds.ComboField, "enum"),
        (kinds.LanguageField, "enum"),
        (kinds.PathField, "path"),
        (kinds.KeymapField, "key"),
    )
    for kind, name in order:
        if isinstance(spec, kind):
            return name

    return "str"


def _unit(spec):
    suffix = getattr(spec, "suffix", None)

    return suffix.strip("()") if suffix else None


def _choices(spec):
    from gridplayer.params.languages import LANGUAGES
    from gridplayer.params.settings_fields import kinds

    if isinstance(spec, kinds.LanguageField):
        return [{"value": lang.code, "label": lang.code} for lang in LANGUAGES]

    if not isinstance(spec, kinds.ComboField):
        return []

    if spec.settings_key == "subtitles/font":
        # the fonts of whatever machine this runs on
        return [{"value": "", "label": "Default"}]

    # the VLC version on this machine, after the decoders' names
    return [
        {"value": _jsonable(value), "label": re.sub(r" <VLC [^>]*>$", "", label)}
        for value, label in spec.choices().items()
    ]


def _depends_on(spec):
    for when in (spec.enabled_when, spec.shown_when, spec.forced_when):
        if when is not None:
            return when.key

    return None


def _condition_note(spec, labels):
    """What the field waits on, in words, where it is more than a checkbox."""

    notes = []
    for name, when in (
        ("Enabled while", spec.enabled_when),
        ("Shown while", spec.shown_when),
    ):
        if when is None:
            continue
        other = labels.get(when.key, when.key)
        if when.values == (True,):
            notes.append(f"{name} {other} is on.")
        else:
            values = ", ".join(_choice_label(when.key, v) for v in when.values)
            notes.append(f"{name} {other} is {values}.")

    if spec.forced_when is not None:
        other = labels.get(spec.forced_when.key, spec.forced_when.key)
        notes.append(f"Forced on while {other} is on.")

    if getattr(spec, "special_text", None):
        notes.append(f"The lowest value is shown as {spec.special_text}.")

    return notes


_CHOICES_BY_KEY = {}


def _choice_label(key, value):
    for choice in _CHOICES_BY_KEY.get(key, []):
        if choice["value"] == _jsonable(value):
            return choice["label"] or repr(choice["value"])

    return str(_jsonable(value))


def _platforms(spec):
    from gridplayer.params import env

    if spec.shown_if is None:
        return []

    saved = env.IS_WINDOWS, env.IS_LINUX, env.IS_MACOS
    shown = []
    try:
        for platform in PLATFORMS:
            env.IS_WINDOWS = platform == "windows"
            env.IS_LINUX = platform == "linux"
            env.IS_MACOS = platform == "macos"
            if spec.shown_if():
                shown.append(platform)
    finally:
        env.IS_WINDOWS, env.IS_LINUX, env.IS_MACOS = saved

    return [] if len(shown) == len(PLATFORMS) else shown


def _macos_labels():
    """The labels that read otherwise on macOS, where the tray is the menu
    bar: the general fields made again as macOS makes them."""

    from gridplayer.params import env
    from gridplayer.params.settings_fields import general

    saved = env.IS_MACOS
    try:
        env.IS_MACOS = True
        importlib.reload(general)
        macos = {f.settings_key: f.label for f in general.GENERAL_FIELDS}
    finally:
        env.IS_MACOS = saved
        importlib.reload(general)

    return macos


def _new_keys(keys):
    """The keys master at BASE_COMMIT has nowhere in its code."""

    new = set()
    for key in keys:
        found = subprocess.run(
            ["git", "grep", "-q", "-F", f'"{key}"', BASE_COMMIT, "--", "gridplayer"],
            cwd=ROOT,
            capture_output=True,
        )
        if found.returncode not in (0, 1):
            raise SystemExit(f"git grep failed: {found.stderr.decode().strip()}")
        if found.returncode == 1:
            new.add(key)

    return new


def _as_on_any_system():
    """What the app works out for this computer, as on one that has it all."""

    from gridplayer.params.settings_fields import advanced
    from gridplayer.utils import screenshots, video_driver

    advanced.is_hw_video_available = lambda: True
    video_driver.is_hw_video_available = lambda: True
    screenshots.get_app_data_dir = lambda: Path("<data folder>")


def collect():
    _offscreen()
    _as_on_any_system()

    from gridplayer.params.settings_fields.kinds import SettingField
    from gridplayer.params.settings_fields.registry import FIELDS
    from gridplayer.params.settings_pages import PAGES
    from gridplayer.settings import _default_settings
    from gridplayer.version import __fork_version__

    rows = []
    for group in PAGES:
        for page in group.pages:
            for item, heading in _walk(page.items, None, []):
                spec = item if isinstance(item, SettingField) else FIELDS[item]
                rows.append((group, page, heading, spec))

    labels = {}
    for _, page, heading, spec in rows:
        labels[spec.settings_key] = spec.label or heading or _plain(page.title)
    for *_, spec in rows:
        _CHOICES_BY_KEY[spec.settings_key] = _choices(spec)

    macos = _macos_labels()
    new = _new_keys([spec.settings_key for *_, spec in rows])

    settings = []
    for group, page, heading, spec in rows:
        key = spec.settings_key
        kind = _type_of(spec)

        tooltip = spec.tooltip() if callable(spec.tooltip) else spec.tooltip
        notes = _condition_note(spec, labels)

        # the GNOME paragraph is only there on Linux
        if tooltip and "\n\nOn GNOME" in tooltip:
            tooltip, gnome = tooltip.split("\n\n", 1)
            notes.append(f"On Linux the tooltip adds: {gnome}")

        if macos.get(key) and macos[key] != spec.label:
            notes.append(f"On macOS the label is {macos[key]}.")
        if key in NOTES:
            notes.append(NOTES[key])

        default = _jsonable(_default_settings[key])
        if key == "player/language":
            default = None

        settings.append(
            {
                "key": key,
                "section": _plain(page.title),
                "group": _plain(group.title),
                "heading": heading,
                "label": labels[key],
                "tooltip": tooltip or None,
                "type": kind,
                "default": default,
                "min": getattr(spec, "minimum", None),
                "max": getattr(spec, "maximum", None),
                "step": (
                    spec.step if kind == "float" else 1 if kind == "int" else None
                ),
                "unit": _unit(spec),
                "choices": _CHOICES_BY_KEY[key],
                "depends_on": _depends_on(spec),
                "platforms": _platforms(spec),
                "since": SINCE_BRANCH if key in new else None,
                "notes": " ".join(notes),
            }
        )

    pages = [
        {
            "id": page.id,
            "title": _plain(page.title),
            "group": _plain(group.title),
            "note": _plain(page.note) if page.note else None,
        }
        for group in PAGES
        for page in group.pages
    ]

    return {
        "schema_version": 1,
        "app_version": __fork_version__,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages": pages,
        "settings": settings,
    }


# ---- docs/reference/settings.md, from the JSON alone


def _md(text):
    if text is None or text == "":
        return ""
    text = str(text).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace("\n", "<br>")


def _code(text):
    return "`" + str(text).replace("|", "\\|") + "`"


def _default_txt(setting):
    default = setting["default"]

    if setting["key"] == "player/language":
        return "System language"
    if setting["type"] == "bool":
        return "On" if default else "Off"
    for choice in setting["choices"]:
        if choice["value"] == default:
            return choice["label"]
    if default in ("", None, {}, []):
        return "(empty)"
    if isinstance(default, list):
        return ", ".join(str(v) for v in default)
    if isinstance(default, float):
        default = f"{default:g}"
    unit = setting["unit"]
    return f"{default} {unit}" if unit else str(default)


def _range_txt(setting):
    if setting["type"] in ("int", "float") and setting["max"] is not None:
        low, high = setting["min"], setting["max"]
        if setting["type"] == "float":
            low, high = f"{low:g}", f"{high:g}"
        unit = f" {setting['unit']}" if setting["unit"] else ""
        return f"{low} to {high}{unit}"

    choices = setting["choices"]
    if not choices:
        return ""
    if len(choices) > 12:
        return f"{len(choices)} choices"
    return ", ".join(c["label"] or "(empty)" for c in choices)


def render_md(data):
    out = [
        "# Settings",
        "",
        (
            "<!-- Generated by tools/gen_tooltips_json.py from docs/tooltips.json."
            " Do not edit by hand. -->"
        ),
        "",
        (
            f"Every setting in the Settings dialog of GridPlayer Alabaster"
            f" {data['app_version']}, page by page, in the order the dialog shows"
            f" them: {len(data['settings'])} settings in all. Tooltip is the text"
            " shown when you point at the setting. Key is the name in"
            " `settings.ini`. Where each value is kept is in the"
            " [full settings reference](settings-reference.md) and"
            " [Where things are stored](storage.md)."
        ),
        "",
        "Settings marked *0.2beta* are new in the 0.2beta branch.",
        "",
    ]

    by_page = {}
    for setting in data["settings"]:
        by_page.setdefault(setting["section"], []).append(setting)

    for page in data["pages"]:
        settings = by_page.get(page["title"], [])
        if not settings:
            continue
        out += [f"## {page['group']}: {page['title']}", ""]
        notes = [n for n in (page["note"], PAGE_NOTES.get(page["id"])) if n]
        if notes:
            out += [_md(" ".join(notes)), ""]
        out += [
            "| Setting | Default | Range or choices | Tooltip | Key |",
            "| --- | --- | --- | --- | --- |",
        ]
        for s in settings:
            label = _md(s["label"])
            if s["heading"] and s["heading"] != s["label"]:
                label = f"{_md(s['heading'])}: {label}"
            if s["since"]:
                label += f" *{s['since']}*"
            if s["platforms"]:
                label += " (" + ", ".join(s["platforms"]) + " only)"
            tip = _md(s["tooltip"])
            if s["notes"]:
                tip = (tip + "<br>" if tip else "") + "*" + _md(s["notes"]) + "*"
            out.append(
                f"| {label} | {_md(_default_txt(s))} | {_md(_range_txt(s))} |"
                f" {tip} | {_code(s['key'])} |"
            )
        out.append("")

    return "\n".join(out)


def main():
    data = collect()

    JSON_TARGET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MD_TARGET.write_text(render_md(data), encoding="utf-8", newline="\n")

    print(
        f"wrote {JSON_TARGET.relative_to(ROOT)} and {MD_TARGET.relative_to(ROOT)}:"
        f" {len(data['settings'])} settings"
    )


if __name__ == "__main__":
    main()
