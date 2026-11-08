$ErrorActionPreference = 'Stop'

# PLACEHOLDER checksum: fill in after the v0.2.0-beta release build (see README.md).
# softwareName matches the Inno UninstallDisplayName "GridPlayer Alabaster", never
# upstream "GridPlayer", so the auto-uninstaller only removes Alabaster.
$packageArgs = @{
  packageName    = $env:ChocolateyPackageName
  fileType       = 'exe'
  softwareName   = 'GridPlayer Alabaster*'
  url64bit       = 'https://github.com/XDevMatt/alabaster-gridplayer/releases/download/v0.2.0-beta/GridPlayer-0.2.0-beta-win64-install.exe'
  checksum64     = 'PLACEHOLDER_SHA256_FILL_AFTER_RELEASE_BUILD'
  checksumType64 = 'sha256'
  # Inno Setup
  silentArgs     = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes = @(0)
}

Install-ChocolateyPackage @packageArgs
