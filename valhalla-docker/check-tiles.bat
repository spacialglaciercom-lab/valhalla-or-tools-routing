@echo off
REM Quick tile check - avoids PowerShell execution policy issues
REM Uses basic Windows commands only

echo ========================================
echo Checking for Valhalla Tiles
echo ========================================
echo.

set "TILE_PATH=D:\valhalla_data"

if not exist "%TILE_PATH%" (
    echo [ERROR] Directory does not exist: %TILE_PATH%
    pause
    exit /b 1
)

echo Checking: %TILE_PATH%
echo.

REM Check for .tar file
echo Checking for .tar archive...
dir /b "%TILE_PATH%\*.tar" >nul 2>&1
if %errorlevel% == 0 (
    echo [FOUND] Tile archive found
    dir /b "%TILE_PATH%\*.tar"
) else (
    echo [NOT FOUND] No .tar files
)
echo.

REM Check for tiles directory
echo Checking for tiles\ directory...
if exist "%TILE_PATH%\tiles" (
    echo [FOUND] Tiles directory exists
    echo Counting files...
    dir /s /b "%TILE_PATH%\tiles\*.gph" 2>nul | find /c /v ""
) else (
    echo [NOT FOUND] No tiles\ subdirectory
)
echo.

REM List directories
echo Directory contents:
dir /b /ad "%TILE_PATH%"
echo.

echo ========================================
echo Check complete
echo ========================================
echo.
echo If no tiles found, run: find-tiles.bat
echo.
pause
