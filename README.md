<p align="center">
  <img src="https://raw.githubusercontent.com/XDevMatt/alabaster-gridplayer/coming-soon/gridplayer-alabaster.png" alt="GridPlayer Alabaster" width="480">
</p>

# GridPlayer Alabaster

GridPlayer Alabaster is a Windows video player that plays many videos at once
in a grid. Each cell has its own file, position, loop, volume, zoom and
playlist. Playback uses VLC (libVLC) through a Python and PyQt5 interface.

**Alabaster 0.2beta - (from GridPlayer 0.5.5).** This is a beta. Release
candidate [v0.2beta_rc1](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1) is out as a prerelease: a portable zip for
Windows 10/11 x64.

## Credit and license

GridPlayer Alabaster is a modified version of
[GridPlayer](https://github.com/vzhd1701/gridplayer) 0.5.5 by Vlad
(vzhd1701). Credit for GridPlayer, and for most of what this program does,
goes to Vlad. Alabaster changes are by XDevMatt.

- Licensed under the GNU General Public License version 3, the same as
  GridPlayer. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
- This is **not the official GridPlayer**. The GridPlayer name and logo belong
  to upstream; the Alabaster name and logo are this project's own.
- Alabaster is **not published on PyPI**. `pip install gridplayer` installs
  upstream GridPlayer.
- Report Alabaster problems in
  [this repository's issues](https://github.com/XDevMatt/alabaster-gridplayer/issues),
  not upstream.

## Windows only

Alabaster supports **Windows 10 and 11 (64-bit)** only. It does not provide or
support macOS or Linux builds, and it does not maintain translations. The
source still contains upstream's cross-platform code, and anyone may port it
under the GPL. If you need macOS, Linux packages or translations that are kept
up to date, use [upstream GridPlayer](https://github.com/vzhd1701/gridplayer).

## Documentation

The full documentation is in [`docs/`](docs/index.md) on the `0.2beta-fixes`
branch:

| Read | For |
| --- | --- |
| [Install on Windows](docs/install.md) | Portable zip (v0.2beta_rc1 prerelease), installer and Chocolatey (not published yet), optional tools. |
| [User guide](docs/USER-GUIDE.md) | Every feature, step by step, on one page. |
| [Topic pages](docs/user-guide/index.md) | One short page per feature. |
| [FAQ and troubleshooting](docs/faq.md) | Common questions and fixes. |
| [Keyboard and mouse shortcuts](docs/reference/keyboard-shortcuts.md) | Every default key, mouse action and unbound command. |
| [Settings](docs/reference/settings.md) | Every setting with default, range and tooltip. |
| [Configuration and files](docs/reference/configuration.md) | Data folder, command line, playlists, per-cell profiles. |
| [Plugins and streaming](docs/PLUGINS-AND-STREAMING.md) | yt-dlp, browser cookies, HLS/DASH, separate audio, SponsorBlock, SubtitleCat.com. |
| [Known limitations](docs/KNOWN-LIMITATIONS.md) | What does not work or is rough. |
| [Future features](docs/FUTURE.md) | What is planned but not built. |

## What Alabaster changes

Compared with GridPlayer 0.5.5 (and upstream's unreleased work that Alabaster
includes), Alabaster adds or changes:

- **Muted start and 3% volume steps.** New cells start muted at 0%, so a full
  grid does not play every soundtrack at once. Mute is volume 0%; the wheel,
  the volume commands and unmute move in steps of 3% (configurable).
- **Subtitle drag and drop.** Drop a subtitle file onto a cell to attach it.
- **Loops.** `[` and `]` set loop start and end; `Shift+L` toggles Loop This
  File and back to the cell's previous When finished action.
- **Rotate to fit** (optional, off by default): turn landscape videos in tall
  cells, and portrait videos in wide cells, to use more of the cell.
- **Other orientation filter**: skip files whose orientation does not match
  the cell (Skip it). An Ask mode exists but is not re-verified.
- **Per-cell profiles** saved in the playlist under stable cell ids.
- **Pictures as slides**, and **Files to play** (All media, Videos only,
  Images only) for folders and stepping; dropped folders follow it.
- **Keep** (`E`, single mode): copy the playing file to a `_keep` folder next
  to its folder, then play the next file.
- **Skip files open in other cells** during random play, on by default.
- **Browser cookies for yt-dlp**: read from your browser at request time;
  nothing is stored. The old cookie file is gone.
- **Streams with separate audio** play in VLC without merging: HLS and DASH
  manifests go to VLC whole, with quality and audio-track menus, and an MP4
  with its own M4A plays with that file attached.
- **Opt-in plugin layer**, with an optional **SubtitleCat.com** search
  (off by default).
- **Shortcuts** entry on the right-click menu, and mouse side buttons that work
  even with click events disabled.
- **Security changes**: JSON single-instance pipe, no local stream relay
  listener, VLC options filtered (no servers, stream output or Lua).
- **Runs next to upstream GridPlayer** with its own settings folder
  (`%APPDATA%\vzhd1701\GridPlayer-Alabaster`) and its own single-instance pipe.

## Getting it

Download the portable zip, `GridPlayer-Alabaster-57f21b1-win64-portable.zip`, from the
[v0.2beta_rc1 prerelease page](https://github.com/XDevMatt/alabaster-gridplayer/releases/tag/v0.2beta_rc1). It is a release candidate for Windows
10 and 11 (64-bit) and is not code-signed, so Windows SmartScreen may warn
before it runs. Extract it into a new folder of its own; it opens as
`GridPlayer-Alabaster-portable\GridPlayer.exe` and does not touch an installed
upstream GridPlayer. See [Install on Windows](docs/install.md).

The installer and the Chocolatey package (`gridplayer-alabaster`) are not
released yet. To run from source instead:

```powershell
uv sync
.\.venv\Scripts\gridplayer.exe
```

You need [uv](https://docs.astral.sh/uv/) and 64-bit VLC 3.0 to run from
source. Packaged builds bundle VLC. See [Building from source](docs/building.md).

### Optional tools (not bundled)

Install and update these yourself:

| Tool | For | Install |
| --- | --- | --- |
| Deno | YouTube's JavaScript challenge (yt-dlp) | `winget install DenoLand.Deno` |
| yt-dlp | A yt-dlp you keep updated, instead of the built-in module | `winget install yt-dlp.yt-dlp` |
| ffmpeg / ffprobe | Planned separate-audio merging; nothing uses them yet | `winget install Gyan.FFmpeg` |

Or with Chocolatey: `choco install deno ffmpeg yt-dlp -y`.

## Quick start

1. Start Alabaster and drag videos or a folder onto the window. Each file gets
   a cell; a folder gets one cell that plays it as a list.
2. Point at a cell and click to play or pause it. Keys act on the cell under
   the mouse pointer.
3. Scroll up over a cell to hear it (new cells start muted).
4. `N` / `B` play the next / previous file in that cell's folder.
5. Double-click a cell for single mode. Right-click for every command, and
   **Shortcuts** to see or change keys.
6. `Ctrl+S` saves the grid as a `.gpls` playlist.

## Attributions

This software was built using

- **Python** by [Python Software Foundation](https://www.python.org/)
  - Licensed under *Python Software Foundation License*
- **Qt** by [Qt Project](https://www.qt.io/)
  - Licensed under *GPL 2.0, GPL 3.0, and LGPL 3.0*
- **VLC** by [VideoLAN](https://www.videolan.org/)
  - Licensed under *GPL 2.0 or later*
- **Deno** by [Deno authors](https://deno.land/)
  - Licensed under *MIT License*
  - Used by yt-dlp for YouTube JavaScript challenges

### Python packages

- **PyQt** by [Riverbank Computing](https://riverbankcomputing.com/)
  - Licensed under *Riverbank Commercial License and GPL v3*
- **python-vlc** by [Olivier Aubert](https://github.com/oaubert/python-vlc)
  - Licensed under *GPL 2.0 and LGPL 2.1*
- **pydantic** by [Samuel Colvin](https://github.com/samuelcolvin/pydantic)
  - Licensed under *MIT License*
- **streamlink** by [Christopher Rosell, Streamlink Team](https://github.com/streamlink/streamlink)
  - Licensed under *BSD-2-Clause License*
- **yt-dlp** by [Contributors](https://github.com/yt-dlp/yt-dlp)
  - Licensed under *Unlicense License*

### Graphics

- **Hack Font** by [Source Foundry](http://sourcefoundry.org/hack/)
  - Licensed under *MIT License*
- **Basic Icons** by [Icongeek26](https://www.flaticon.com/authors/icongeek26)
  - Licensed under *Flaticon License*
- **Suru Icons** by [Sam Hewitt](https://snwh.org/)
  - Licensed under *Creative Commons Attribution-Share Alike 4.0*
- **Clean App Download Buttons** by [Tony Thomas](https://medialoot.com/item/clean-app-download-buttons/)
  - Licensed under *MediaLoot License*
- **Flag Icons** by [Panayiotis Lipiridis](https://github.com/lipis/flag-icons)
  - Licensed under *MIT License*
- **Lucide Icons** by [Lucide Contributors](https://lucide.dev/)
  - Licensed under *ISC License*

### Data

- **SponsorBlock** by [Ajay Ramachandran and contributors](https://sponsor.ajay.app/)
  - Licensed under *CC BY-NC-SA 4.0*

## Translations (from upstream GridPlayer)

The translations shipped with Alabaster are upstream GridPlayer's, made by these
contributors through upstream's Crowdin project. Alabaster does not maintain
translations, and text added by Alabaster is English only.

<!-- CROWDIN-CONTRIBUTORS-START -->

<table>
  <tbody>
    <tr>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/VenusGirl"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/14432528/medium/3284b34db4ef3cda16835c5a18c797d0.jpg" />
          <br />
          <sub><b>VenusGirl</b></sub></a>
        <br />
        <sub><b>886 words</b></sub>
        <br /><sub><b><code title="Korean">ko</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/LOUIS_Sylvain"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/14983555/medium/af7d7ab185011ffda0bd01b41fc05ccf.png" />
          <br />
          <sub><b>Sylvain LOUIS</b></sub>
          <br />
          <sub><b>(LOUIS_Sylvain)</b></sub></a>
        <br />
        <sub><b>886 words</b></sub>
        <br /><sub><b><code title="French">fr</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Gabriel-BS1"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15681015/medium/50b012437410a2a9c27236c0ce05b1b1.png" />
          <br />
          <sub><b>GBS ~ TECH</b></sub>
          <br />
          <sub><b>(Gabriel-BS1)</b></sub></a>
        <br />
        <sub><b>886 words</b></sub>
        <br /><sub><b><code title="Portuguese, Brazilian">pt-BR</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Granberg"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/12416181/medium/2864d29be808543d56f9e210a06ad934.jpg" />
          <br />
          <sub><b>Göran</b></sub>
          <br />
          <sub><b>(Granberg)</b></sub></a>
        <br />
        <sub><b>875 words</b></sub>
        <br /><sub><b><code title="Swedish">sv-SE</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/royhendum"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/17390478/medium/ab5a65a9b43bbae930fe45baa1a5e51f.png" />
          <br />
          <sub><b>Roy Hendum</b></sub>
          <br />
          <sub><b>(royhendum)</b></sub></a>
        <br />
        <sub><b>875 words</b></sub>
        <br /><sub><b><code title="Norwegian">no</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/zxas"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/16338184/medium/90d1c13645360de47426fcd50d7630df.jpeg" />
          <br />
          <sub><b>z Z</b></sub>
          <br />
          <sub><b>(zxas)</b></sub></a>
        <br />
        <sub><b>851 words</b></sub>
        <br /><sub><b><code title="Chinese Traditional">zh-TW</code></b></sub>
      </td>
    </tr>
    <tr>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/davidev1"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/13229273/medium/03b55ef5010bbc801f432e51e4a50171.jpg" />
          <br />
          <sub><b>Davide V.</b></sub>
          <br />
          <sub><b>(davidev1)</b></sub></a>
        <br />
        <sub><b>752 words</b></sub>
        <br /><sub><b><code title="Italian">it</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Vistaus"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/12732621/medium/bbca85454e90b7362cbbe57e5cd54489.jpeg" />
          <br />
          <sub><b>Heimen Stoffels</b></sub>
          <br />
          <sub><b>(Vistaus)</b></sub></a>
        <br />
        <sub><b>751 words</b></sub>
        <br /><sub><b><code title="Dutch">nl</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/japanese.john.doe.774"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15405594/medium/1e457ad578b4390a744f8b1af85533fa.png" />
          <br />
          <sub><b>七篠孝志</b></sub>
          <br />
          <sub><b>(japanese.john.doe.774)</b></sub></a>
        <br />
        <sub><b>751 words</b></sub>
        <br /><sub><b><code title="Japanese">ja</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/DominikPott"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15472688/medium/6e48ea2f0a8564252086d2d7775d2f21.png" />
          <br />
          <sub><b>DominikPott</b></sub></a>
        <br />
        <sub><b>751 words</b></sub>
        <br /><sub><b><code title="German">de</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Azoaz6001"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15591465/medium/ae7a5aafbc99dc9ac4ba3a8c5bf42dcb_default.png" />
          <br />
          <sub><b>Azoaz6001</b></sub></a>
        <br />
        <sub><b>751 words</b></sub>
        <br /><sub><b><code title="Arabic">ar</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/wyg945"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15682575/medium/e3d1504b9b88be18745f758cb4f11d77.png" />
          <br />
          <sub><b>Yagang Wang</b></sub>
          <br />
          <sub><b>(wyg945)</b></sub></a>
        <br />
        <sub><b>751 words</b></sub>
        <br /><sub><b><code title="Chinese Simplified">zh-CN</code></b></sub>
      </td>
    </tr>
    <tr>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Golbinex"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/17664878/medium/1b0e9f044a085950575bcf53e3581336.jpeg" />
          <br />
          <sub><b>Kryštof Baksa</b></sub>
          <br />
          <sub><b>(Golbinex)</b></sub></a>
        <br />
        <sub><b>674 words</b></sub>
        <br /><sub><b><code title="Czech">cs</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/IngrownMink4"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/14414288/medium/53f8a637c2fa88786f85808ebee55807.jpg" />
          <br />
          <sub><b>Sergio Varela</b></sub>
          <br />
          <sub><b>(IngrownMink4)</b></sub></a>
        <br />
        <sub><b>652 words</b></sub>
        <br /><sub><b><code title="Spanish">es-ES</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/fifi132"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15774079/medium/0e0d2651e73807bbb9050e8fd3e44f18.png" />
          <br />
          <sub><b>rafal132</b></sub>
          <br />
          <sub><b>(fifi132)</b></sub></a>
        <br />
        <sub><b>598 words</b></sub>
        <br /><sub><b><code title="Polish">pl</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/a2942"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/16794451/medium/184acbf1f2f0e4adf1dc62822bd5acfd.jpg" />
          <br />
          <sub><b>a2942</b></sub></a>
        <br />
        <sub><b>496 words</b></sub>
        <br /><sub><b><code title="Chinese Simplified">zh-CN</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/LiberiFatali"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15598851/medium/610ee0a4acb813a2832ac2c927e79cfb_default.png" />
          <br />
          <sub><b>LiberiFatali</b></sub></a>
        <br />
        <sub><b>456 words</b></sub>
        <br /><sub><b><code title="Vietnamese">vi</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/samu112"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15157130/medium/e119d6e287f4e49464eac1ee32974bac_default.png" />
          <br />
          <sub><b>samu112</b></sub></a>
        <br />
        <sub><b>438 words</b></sub>
        <br /><sub><b><code title="Hungarian">hu</code></b></sub>
      </td>
    </tr>
    <tr>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/asolis2020"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15661045/medium/6ba336a35aa362fa47b5adf11919141b_default.png" />
          <br />
          <sub><b>asolis2020</b></sub></a>
        <br />
        <sub><b>266 words</b></sub>
        <br /><sub><b><code title="Spanish">es-ES</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/SolarCTP"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15384684/medium/f0197a7e2769ecc2788a18091a7afb0b.png" />
          <br />
          <sub><b>SolarCTP</b></sub></a>
        <br />
        <sub><b>164 words</b></sub>
        <br /><sub><b><code title="Italian">it</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/PrinceNorris"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/13962625/medium/907539fd79ca32a8a08d400a1aa043f7_default.png" />
          <br />
          <sub><b>Sebastian Jasiński</b></sub>
          <br />
          <sub><b>(PrinceNorris)</b></sub></a>
        <br />
        <sub><b>163 words</b></sub>
        <br /><sub><b><code title="Polish">pl</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/reiss404"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/17071680/medium/8b927c3a2c3389c590128dc1f89dbeab.jpeg" />
          <br />
          <sub><b>Manuel</b></sub>
          <br />
          <sub><b>(reiss404)</b></sub></a>
        <br />
        <sub><b>133 words</b></sub>
        <br /><sub><b><code title="German">de</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/aportuguesecoder"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/17032790/medium/7ae1612b2227266f02dd7c6af1bb0d67.jpeg" />
          <br />
          <sub><b>Armando Gomes</b></sub>
          <br />
          <sub><b>(aportuguesecoder)</b></sub></a>
        <br />
        <sub><b>121 words</b></sub>
        <br /><sub><b><code title="Portuguese">pt-PT</code></b></sub>
      </td>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/Akronos"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/16284890/medium/db02e5c7b29dce08b02cd94a93b0ef0e_default.png" />
          <br />
          <sub><b>Akronos</b></sub></a>
        <br />
        <sub><b>112 words</b></sub>
        <br /><sub><b><code title="Czech">cs</code></b></sub>
      </td>
    </tr>
    <tr>
      <td align="center" valign="top">
        <a href="https://crowdin.com/profile/WackyFox"><img alt="logo" style="width: 64px" src="https://crowdin-static.cf-downloads.crowdin.com/avatar/15807071/medium/21329dc32cf56b0743914d5ef724d1e3.jpeg" />
          <br />
          <sub><b>Владимир Ларин</b></sub>
          <br />
          <sub><b>(WackyFox)</b></sub></a>
        <br />
        <sub><b>108 words</b></sub>
        <br /><sub><b><code title="Hebrew">he</code></b></sub>
      </td>
    </tr>
  </tbody>
</table>
<!-- CROWDIN-CONTRIBUTORS-END -->

## How it's made

XDevMatt: where Matt (Monster Energy edition) and American superintelligence (Grok Bot & Grok Build 4.7) stop pretending there's a clean line between them. Collaborative work, proudly hybrid.

## License

This software is licensed under the terms of the GNU General Public License
version 3 (GPLv3). The full text is in [LICENSE](LICENSE) and
[online](https://www.gnu.org/licenses/gpl-3.0.html).

GridPlayer Alabaster is a modified version of GridPlayer by vzhd1701.
Modifications are Copyright (C) 2026 XDevMatt and are licensed under the same
terms; see [NOTICE](NOTICE).
