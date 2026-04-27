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

# 6. Zip + done
$exe = "dist\VEO_Pipeline_Pro\VEO_Pipeline_Pro.exe"
if (Test-Path $exe) {
    Compress-Archive -Path dist\VEO_Pipeline_Pro\* -DestinationPath dist\VEO_Pipeline_Pro_Windows.zip -Force -CompressionLevel Optimal
    $size = (Get-Item dist\VEO_Pipeline_Pro_Windows.zip).Length / 1MB
    Write-Host ("`n✅ Build OK: dist\VEO_Pipeline_Pro_Windows.zip ({0:N1} MB)" -f $size) -ForegroundColor Green
    Write-Host "Extract zip + double-click VEO_Pipeline_Pro.exe" -ForegroundColor Cyan
    Write-Host "Onedir mode = 3-5x faster startup than onefile." -ForegroundColor Cyan
} else {
    Write-Host "❌ Build failed — see logs above" -ForegroundColor Red
    exit 1
}
