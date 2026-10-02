$ErrorActionPreference = "Stop"
$fontsDir = Join-Path $PSScriptRoot "..\fonts"
New-Item -ItemType Directory -Force -Path $fontsDir | Out-Null
$url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
$dest = Join-Path $fontsDir "DejaVuSans.ttf"
Invoke-WebRequest -Uri $url -OutFile $dest
Write-Host "Saved: $dest"
