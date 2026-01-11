@echo off
REM Automated startup script for Valhalla Docker
REM This script starts Valhalla automatically with your tiles from D:\valhalla_data
REM Fixes PowerShell execution policy issues

echo ========================================
echo Valhalla Docker - Automated Startup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Quick tile check
echo Checking for tiles in D:\valhalla_data...
if exist "D:\valhalla_data\valhalla_tiles.tar" (
    echo [OK] Found tile archive
) else if exist "D:\valhalla_data\tiles" (
    echo [OK] Found tiles directory
) else (
    echo [WARNING] No tiles found in expected locations
    echo Run find-tiles.bat to locate your tiles
    echo.
)
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Starting Valhalla service...
echo Tiles location: D:\valhalla_data
echo API will be available at: http://localhost:8002
echo.

REM Start the service
docker-compose up -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Valhalla service
    echo.
    echo Troubleshooting:
    echo 1. Ensure Docker Desktop has access to D: drive
    echo    Settings -^> Resources -^> File Sharing -^> Add D:
    echo 2. Check that tiles exist in D:\valhalla_data
    echo 3. View logs: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Valhalla service is starting...
echo.
echo Waiting for service to be ready...
timeout /t 5 /nobreak >nul

REM Check if service is responding
curl -s http://localhost:8002/status >nul 2>&1
if errorlevel 1 (
    echo Service is starting (this may take 30-60 seconds)...
    echo.
    echo To check status: curl http://localhost:8002/status
    echo To view logs: docker-compose logs -f
) else (
    echo [SUCCESS] Valhalla is ready!
    echo.
    echo API Status: http://localhost:8002/status
    echo.
)

echo.
echo Useful commands:
echo   View logs:    docker-compose logs -f
echo   Stop service: docker-compose down
echo   Check status: curl http://localhost:8002/status
echo.
pause
