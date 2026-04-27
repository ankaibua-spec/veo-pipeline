# Windows build script for VEO Pipeline Pro
# Run from repo root: powershell -ExecutionPolicy Bypass -File build/build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== VEO Pipeline Pro Builder ===" -ForegroundColor Cyan

# 1. Ensure venv
if (!(Test-Path ".venv")) {
    Write-Host "Creating venv..." -ForegroundColor Yellow
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1

# 2. Install deps
Write-Host "Installing deps..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install pyinstaller PyQt6 playwright requests urllib3 watchdog google-api-python-client google-auth google-auth-oauthlib

# 3. Install Playwright browsers (skipped at runtime — user installs separately)
# python -m playwright install chromium

# 4. Clean old build
Remove-Item -Recurse -Force build\dist, build\build, dist, build_output -ErrorAction SilentlyContinue

# 5. Build
Write-Host "Building exe..." -ForegroundColor Yellow
pyinstaller --clean --distpath dist --workpath build/work build/veo-pipeline-pro.spec

# 6. Done
$exe = "dist\VEO_Pipeline_Pro.exe"
if (Test-Path $exe) {
    $size = (Get-Item $exe).Length / 1MB
    Write-Host ("`n✅ Build OK: {0} ({1:N1} MB)" -f $exe, $size) -ForegroundColor Green
    Write-Host "Distribute this single file. Users double-click to run." -ForegroundColor Cyan
} else {
    Write-Host "❌ Build failed — see logs above" -ForegroundColor Red
    exit 1
}
