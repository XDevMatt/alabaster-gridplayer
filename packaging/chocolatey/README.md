# Chocolatey package: gridplayer-alabaster

Draft package for GridPlayer Alabaster 0.2beta, "Alabaster 0.2beta - (from GridPlayer 0.5.5)".
Package version `0.2.0-beta`, from the GitHub pre-release `v0.2.0-beta`.
The package downloads the Inno Setup installer and runs it silently with
`/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-`. Uninstall uses the Chocolatey
auto-uninstaller (the Inno Setup uninstall entry matched by `softwareName`).

VLC is bundled with the app. The package has no dependencies.

## Optional tools

ffmpeg, yt-dlp and Deno are not bundled and are not package dependencies.
Install and update them yourself:

```
choco install deno ffmpeg yt-dlp -y
choco upgrade deno ffmpeg yt-dlp -y
```

Or with winget: `winget install Gyan.FFmpeg`, `winget install yt-dlp.yt-dlp`,
`winget install DenoLand.Deno`.

## Fill in the URL and checksum after the release build

1. Build the Windows release (`scripts/windows/build_packages.sh`) and publish
   the GitHub pre-release `v0.2.0-beta`. The installer is named
   `$APP_NAME-$APP_FILE_VERSION-win64-install.exe`.
2. In `tools/chocolateyinstall.ps1`, check that `url64bit` matches the real asset
   name (the draft assumes `GridPlayer-0.2.0-beta-win64-install.exe`).
3. Get the SHA256: `Get-FileHash .\GridPlayer-0.2.0-beta-win64-install.exe -Algorithm SHA256`,
   or read the asset digest on the release page.
4. Replace `PLACEHOLDER_SHA256_FILL_AFTER_RELEASE_BUILD` in
   `tools/chocolateyinstall.ps1` and `tools/VERIFICATION.txt`.

## Test locally (Windows, admin shell)

```
cd packaging\chocolatey
choco pack
choco install gridplayer-alabaster --source . --pre -y
choco uninstall gridplayer-alabaster -y
```

## Push

```
choco apikey add -s https://push.chocolatey.org/ -k YOUR_API_KEY
choco push gridplayer-alabaster.0.2.0-beta.nupkg --source https://push.chocolatey.org/
```

Packages on the community repository go through moderation (automated
validation, verification, then human review) before they are public, which
can take days. Pre-release versions install only with `--pre`.
