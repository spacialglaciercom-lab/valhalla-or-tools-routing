@echo off
REM Quick verification script - checks if Valhalla is running

echo Checking Valhalla service...
echo.

curl -s http://localhost:8002/status >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Valhalla is not responding
    echo.
    echo Is the service running?
    echo   Check: docker-compose ps
    echo   Start: docker-compose up -d
    echo   Logs:  docker-compose logs
) else (
    echo [SUCCESS] Valhalla is running!
    echo.
    echo Testing status endpoint...
    curl -s http://localhost:8002/status
    echo.
    echo.
    echo Service is ready at: http://localhost:8002
)

pause
