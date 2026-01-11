# PowerShell script to find Valhalla tiles in D:\valhalla_data
# This script searches for tiles in various locations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Valhalla Tile Finder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$tilePath = "D:\valhalla_data"
$found = $false

Write-Host "Searching for tiles in: $tilePath" -ForegroundColor Yellow
Write-Host ""

# Check if directory exists
if (-not (Test-Path $tilePath)) {
    Write-Host "[ERROR] Directory does not exist: $tilePath" -ForegroundColor Red
    exit 1
}

# Check for .tar file
Write-Host "Checking for tile archive..." -ForegroundColor Cyan
$tarFiles = Get-ChildItem -Path $tilePath -Filter "*.tar" -ErrorAction SilentlyContinue
if ($tarFiles) {
    Write-Host "[FOUND] Tile archive(s):" -ForegroundColor Green
    foreach ($file in $tarFiles) {
        $size = [math]::Round($file.Length / 1GB, 2)
        Write-Host "  - $($file.Name) ($size GB)" -ForegroundColor Green
        $found = $true
    }
} else {
    Write-Host "[NOT FOUND] No .tar files" -ForegroundColor Yellow
}
Write-Host ""

# Check for tiles directory
Write-Host "Checking for tiles directory..." -ForegroundColor Cyan
$tilesDir = Join-Path $tilePath "tiles"
if (Test-Path $tilesDir) {
    Write-Host "[FOUND] Tiles directory: $tilesDir" -ForegroundColor Green
    
    # Count .gph files recursively
    $gphFiles = Get-ChildItem -Path $tilesDir -Filter "*.gph" -Recurse -ErrorAction SilentlyContinue
    if ($gphFiles) {
        $count = ($gphFiles | Measure-Object).Count
        $totalSize = ($gphFiles | Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($totalSize / 1GB, 2)
        Write-Host "  Found $count .gph files ($sizeGB GB total)" -ForegroundColor Green
        $found = $true
    } else {
        Write-Host "  [WARNING] Tiles directory exists but no .gph files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "[NOT FOUND] No tiles/ subdirectory" -ForegroundColor Yellow
}
Write-Host ""

# Check root directory for .gph files
Write-Host "Checking root directory for .gph files..." -ForegroundColor Cyan
$rootGph = Get-ChildItem -Path $tilePath -Filter "*.gph" -ErrorAction SilentlyContinue
if ($rootGph) {
    $count = ($rootGph | Measure-Object).Count
    Write-Host "[FOUND] $count .gph files in root directory" -ForegroundColor Green
    $found = $true
} else {
    Write-Host "[NOT FOUND] No .gph files in root" -ForegroundColor Yellow
}
Write-Host ""

# List all directories
Write-Host "Directory structure:" -ForegroundColor Cyan
Get-ChildItem -Path $tilePath -Directory | ForEach-Object {
    Write-Host "  - $($_.Name)/" -ForegroundColor Gray
}
Write-Host ""

# Summary
if ($found) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Tiles found!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The Docker setup should work with these tiles." -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "[ERROR] No tiles found!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Expected one of:" -ForegroundColor Yellow
    Write-Host "  1. D:\valhalla_data\valhalla_tiles.tar" -ForegroundColor Yellow
    Write-Host "  2. D:\valhalla_data\tiles\ (with .gph files)" -ForegroundColor Yellow
    Write-Host "  3. D:\valhalla_data\*.gph files" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
