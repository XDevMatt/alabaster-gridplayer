# Fetch official Deno Windows x64 into vendor/deno. Not committed.
$ErrorActionPreference = "Stop"
$Version = "v2.5.6"
$Asset = "deno-x86_64-pc-windows-msvc.zip"
$Url = "https://github.com/denoland/deno/releases/download/$Version/$Asset"
$Root = Split-Path -Parent $PSScriptRoot
$Dest = Join-Path $Root "vendor\deno"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$Zip = Join-Path $Dest $Asset
Write-Host "Downloading $Url"
Invoke-WebRequest -Uri $Url -OutFile $Zip
Expand-Archive -Path $Zip -DestinationPath $Dest -Force
$Exe = Join-Path $Dest "deno.exe"
$Hash = (Get-FileHash -Algorithm SHA256 $Exe).Hash.ToLower()
Write-Host "Deno $Version"
Write-Host "SHA-256 $Hash"
Set-Content -Path (Join-Path $Dest "SHA256") -Value "$Hash  deno.exe"
