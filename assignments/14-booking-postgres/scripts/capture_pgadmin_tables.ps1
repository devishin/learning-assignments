# Скриншот 01: окно pgAdmin с таблицами booking (после импорта servers.json).
$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$shots = Join-Path $root "screenshots"
$pg = Join-Path $env:LOCALAPPDATA "Programs\pgAdmin 4\runtime\pgAdmin4.exe"
if (-not (Test-Path $pg)) { throw "pgAdmin не найден: $pg" }

Start-Process $pg
Start-Sleep -Seconds 12
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::new([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Forms.Screen]::PrimaryScreen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
$out = Join-Path $shots "01_pgadmin_tables.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host "saved $out (откройте сервер booking-docker и View Data, переснимите при необходимости)"