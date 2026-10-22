# Pinned Deno (not committed)

GridPlayer passes yt-dlp only this folder's `deno.exe` unless
`streaming/js_runtime_allow_path` is on.

## Fetch (Windows x64)

Release: https://github.com/denoland/deno/releases/tag/v2.5.6

Asset: `deno-x86_64-pc-windows-msvc.zip`

```powershell
$zip = "vendor/deno/deno-x86_64-pc-windows-msvc.zip"
Invoke-WebRequest -Uri "https://github.com/denoland/deno/releases/download/v2.5.6/deno-x86_64-pc-windows-msvc.zip" -OutFile $zip
# Verify SHA-256 against the checksums published on that GitHub release, then:
Expand-Archive $zip -DestinationPath vendor/deno -Force
```

Fetched here on 2026-10-22:

- version: v2.5.6
- SHA-256: `3e367a556068d04e02854add2295a68e7f1cfe6e3e1353027907fd3a0f1b8580`

Do not commit the binary.
