"""Opt-in plugins. A plugin module is imported only while its setting is on.

Nothing here reaches the network, and nothing here holds cookies. The
catalog is data: module paths, not imports.
"""

import importlib

from gridplayer.plugins.base import PluginSpec
from gridplayer.settings import Settings

# Streamlink is not an entry. Its resolver stays where it is until a
# later pass registers it as kind "resolver".
CATALOG = (
    PluginSpec(
        id="subtitlecat",
        module="gridplayer.plugins.subtitlecat",
        setting="plugins/subtitlecat",
        kind="subtitles",
    ),
)


def spec_for(plugin_id: str) -> PluginSpec | None:
    for spec in CATALOG:
        if spec.id == plugin_id:
            return spec
    return None


def is_enabled(spec: PluginSpec) -> bool:
    try:
        return bool(Settings().get(spec.setting))
    except (KeyError, ValueError, TypeError):
        return False


def load(plugin_id: str):
    """The plugin module, or None when it is off or unknown.

    Off returns before import. Callers that need a dialog import that
    themselves, after this says the plugin is on.
    """

    spec = spec_for(plugin_id)

    if spec is None or not is_enabled(spec):
        return None

    return importlib.import_module(spec.module)
