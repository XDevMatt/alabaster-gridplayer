GridPlayer Alabaster - Windows x64 portable

Unzip the whole archive into a NEW folder of your own, then open
GridPlayer-Alabaster-portable\GridPlayer.exe. Do not copy these files over
an existing GridPlayer install. Keep lib, libVLC and portable_data beside
the executable. No Python or separately installed VLC is needed.

This is GridPlayer Alabaster, not official GridPlayer. It is built from
Vlad (vzhd1701)'s GridPlayer 0.5.5 under GNU GPLv3. See LICENSE and NOTICE.
Source: https://github.com/XDevMatt/alabaster-gridplayer/tree/0.2beta-fixes
The exact application source is included in source\Alabaster-source.zip.
This is an unsigned development build; BUILD.json records its source commit
and dependencies. It is not a Microsoft Store or signed release installer.

This portable does not install anything, register file associations, write
an uninstall entry, remove files from Program Files, or uninstall upstream
GridPlayer. Its separate folder keeps it apart from upstream GridPlayer.
Its single-instance channel is gridplayer-alabaster-fileopen, not upstream's.
Settings, logs and cache live in portable_data beside GridPlayer.exe.
A GP_USER_DATA_DIR environment override takes precedence if you set one.
Without portable_data, settings use the separate GridPlayer-Alabaster data
folder under the Windows roaming application-data folder, not GridPlayer.
Delete this portable folder to remove the app (back up settings first).

Local playback includes libVLC. Deno is needed for YouTube JavaScript
challenges; install it separately if you use those streams. yt-dlp is
bundled as a Python module. FFmpeg is not bundled; separate-audio merging
is not implemented by this build. Read docs\KNOWN-LIMITATIONS.md and the
user guide for current limitations. Streaming was not exhaustively tested.
