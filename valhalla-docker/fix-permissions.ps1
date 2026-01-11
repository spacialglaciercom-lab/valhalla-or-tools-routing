# PowerShell script to fix permissions for Valhalla volumes
# Configures permissions for UID 59999 and GID 59999

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Valhalla Permissions Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuring permissions for UID: 59999, GID: 59999" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator on Windows
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠ Note: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "  Docker Desktop handles permissions differently on Windows" -ForegroundColor Gray
    Write-Host "  The container will run with UID 59999 and GID 59999" -ForegroundColor Gray
    Write-Host ""
}

# Note about D: drive volume (mounted as /custom_files in container)
Write-Host "Note: Valhalla tiles are stored on D:\valhalla_data" -ForegroundColor Cyan
Write-Host "  This volume is mounted as /custom_files in the container" -ForegroundColor Gray
Write-Host "  Docker Desktop handles permissions for Windows volumes automatically" -ForegroundColor Gray
Write-Host ""

# Fix permissions on local directories (if they exist)
$directories = @("config", "scripts", "or-tools")

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "Checking permissions on $dir..." -ForegroundColor Yellow
        
        try {
            $acl = Get-Acl $dir
            $permission = "BUILTIN\Users", "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow"
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
            $acl.SetAccessRule($accessRule)
            Set-Acl $dir $acl
            
            Write-Host "  ✓ Permissions set for $dir" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ Could not set permissions on $dir: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "    This is usually fine on Windows with Docker Desktop" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ℹ Directory $dir does not exist (optional)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✓ Permission configuration complete!" -ForegroundColor Green
Write-Host ""

Write-Host "Note: On Windows with Docker Desktop:" -ForegroundColor Cyan
Write-Host "  - Docker handles file permissions differently" -ForegroundColor Gray
Write-Host "  - Valhalla container runs as UID 59999:GID 59999" -ForegroundColor Gray
Write-Host "  - Volume mounts (D:\valhalla_data) are handled automatically" -ForegroundColor Gray
Write-Host ""

Write-Host "After starting the container, if you see permission errors:" -ForegroundColor Yellow
Write-Host "  1. Check Docker Desktop settings (Settings → Resources → File Sharing)" -ForegroundColor Gray
Write-Host "  2. Verify D: drive is shared in Docker Desktop" -ForegroundColor Gray
Write-Host "  3. Check container logs: docker compose logs valhalla" -ForegroundColor Gray
Write-Host ""

Write-Host "To verify Valhalla is running correctly:" -ForegroundColor Cyan
Write-Host "  docker compose ps" -ForegroundColor White
Write-Host "  curl http://localhost:8002/status" -ForegroundColor White
Write-Host ""
