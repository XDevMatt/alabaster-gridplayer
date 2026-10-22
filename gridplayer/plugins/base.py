"""What a plugin is. The host keeps no cookie jar for one to share."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginSpec:
    """One opt-in plugin.

    ``kind`` is ``subtitles`` for SubtitleCat. A later pass can register
    Streamlink with ``kind`` ``resolver`` without this layer growing a
    shared cookie jar. Streamlink stays where it is for now.
    """

    id: str
    module: str
    setting: str
    kind: str
