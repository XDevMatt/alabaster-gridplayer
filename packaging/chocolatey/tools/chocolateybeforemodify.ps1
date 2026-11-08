$ErrorActionPreference = 'SilentlyContinue'

# Close running GridPlayer Alabaster before upgrade or uninstall. The program
# file is GridPlayer.exe, the same name as upstream GridPlayer's, so match on
# Alabaster's install folder and never stop upstream GridPlayer.
$installDir = Join-Path $env:ProgramFiles 'GridPlayer Alabaster'
$uninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{5E9EFBF1-5CB1-4898-BF59-6CA87176891D}_is1'
foreach ($root in 'HKLM:', 'HKCU:') {
  $location = (Get-ItemProperty -Path "$root\$uninstallKey" -ErrorAction SilentlyContinue).InstallLocation
  if ($location) { $installDir = $location; break }
}
$installDir = $installDir.TrimEnd('\') + '\'

Get-Process -Name 'GridPlayer' -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -and $_.Path.StartsWith($installDir, [System.StringComparison]::OrdinalIgnoreCase) } |
  Stop-Process -Force -ErrorAction SilentlyContinue
