__app_name__ = "GridPlayer"
__display_name__ = "GridPlayer Alabaster"
__author_name__ = "vzhd1701"
__author_contact__ = "vzhd1701@gmail.com"
__app_id__ = "com.vzhd1701.gridplayer"
__version__ = "0.5.5"
__version_date__ = "2026-07-24"
# The fork's repository: the one place to change when the repo moves.
# A literal string: scripts/init_app_vars.sh reads it with sed.
__app_url__ = "https://github.com/XDevMatt/gridplayer-alabaster"
__app_license_url__ = "https://www.gnu.org/licenses/gpl-3.0.html"
# bug reports go to the fork, never to upstream; nothing is sent by the app
__app_bugtracker_url__ = f"{__app_url__}/issues"
__app_new_issue_url__ = f"{__app_url__}/issues/new"

# GridPlayer Alabaster is a modified version of GridPlayer by vzhd1701.
# __app_name__, __author_name__ and __app_id__ above stay upstream's (app ids,
# build scripts, log file name).
# The fork's own settings folder and single-instance pipe, so it runs next to
# upstream GridPlayer without sharing settings or catching its files. Do not
# revert these when merging upstream.
# Qt application name, so the settings folder is
# %APPDATA%\vzhd1701\GridPlayer-Alabaster (upstream: ...\GridPlayer)
__settings_name__ = "GridPlayer-Alabaster"
# \\.\pipe\<name> on Windows, <name>.socket on Linux (upstream: gridplayer-fileopen)
__instance_name__ = "gridplayer-alabaster-fileopen"
__upstream_name__ = "GridPlayer"
__upstream_author__ = "vzhd1701"
__upstream_url__ = "https://github.com/vzhd1701/gridplayer"
__upstream_version__ = __version__
__fork_author__ = "XDevMatt"
__fork_version__ = f"{__version__}-alabaster.1"
