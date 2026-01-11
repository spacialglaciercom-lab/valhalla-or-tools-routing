@echo off
REM Batch wrapper for PowerShell tile finder script
REM This avoids PowerShell execution policy issues

powershell.exe -ExecutionPolicy Bypass -File "%~dp0find-tiles.ps1"

pause
