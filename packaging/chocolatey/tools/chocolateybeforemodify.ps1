$ErrorActionPreference = 'SilentlyContinue'
Get-Process 'GridPlayer*' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
