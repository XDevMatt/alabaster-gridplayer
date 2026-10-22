"""Find subtitles for this cell on SubtitleCat.

The plugin package is imported only when the user asks and the setting
is on. While it is off, this module does not import it.
"""

from gridplayer.widgets.video_block_guards import VideoBlockPart


class SubtitleCatControl(VideoBlockPart):
    def find(self):
        from gridplayer.plugins import load

        if load("subtitlecat") is None:
            return None

        from gridplayer.plugins.subtitlecat.dialog import SubtitleCatDialog

        dialog = SubtitleCatDialog(self._block, parent=self._block.window())
        dialog.exec_()
        return None
