# Troubleshooting Guide

## PowerShell Execution Policy Error

If you get errors like "cannot be loaded because running scripts is disabled":

### Quick Fix:
All `.bat` files now bypass execution policy automatically. Just run:
```batch
start.bat
```

### Manual Fix:
```powershell
# Run this once to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Finding Your Tiles

### Option 1: Use the tile finder (recommended)
```batch
find-tiles.bat
```
This will search for tiles in all common locations.

### Option 2: Quick check (no PowerShell)
```batch
check-tiles.bat
```

### Option 3: Manual check
```powershell
# Check for .tar file
dir D:\valhalla_data\*.tar

# Check for tiles directory
dir D:\valhalla_data\tiles

# Count .gph files recursively
Get-ChildItem "D:\valhalla_data" -Filter "*.gph" -Recurse | Measure-Object
```

## Common Tile Locations

Valhalla tiles can be in different structures:

### Structure 1: Tile Archive
```
D:\valhalla_data\
└── valhalla_tiles.tar
```

### Structure 2: Tiles Directory
```
D:\valhalla_data\
└── tiles\
    ├── 0\
    │   ├── 000\
    │   │   └── 000.gph
    │   └── 001\
    └── 1\
```

### Structure 3: Root Level Tiles
```
D:\valhalla_data\
├── 0\
├── 1\
└── *.gph files
```

## Docker Can't Find Tiles

### Check inside container:
```powershell
docker-compose exec valhalla ls -lh /custom_files/
docker-compose exec valhalla find /custom_files -name "*.gph" | head -5
```

### Verify mount:
```powershell
docker-compose exec valhalla ls -lh /custom_files/valhalla_tiles.tar
# OR
docker-compose exec valhalla ls -lh /custom_files/tiles/
```

## Service Won't Start

### Check logs:
```powershell
docker-compose logs valhalla
docker-compose logs --tail=50 valhalla
```

### Common errors:

**Error: No tiles found**
- Solution: Run `find-tiles.bat` to locate your tiles
- Ensure tiles are in `D:\valhalla_data` or subdirectory

**Error: Permission denied**
- Solution: Docker Desktop → Settings → Resources → File Sharing → Add D:

**Error: Cannot access D: drive**
- Solution: Ensure Docker Desktop has D: drive shared (see above)

## API Not Responding

### Check service status:
```powershell
curl http://localhost:8002/status
```

### Check container health:
```powershell
docker-compose ps
```

### Restart service:
```powershell
docker-compose restart valhalla
```

## Still Having Issues?

1. **Run diagnostics:**
   ```batch
   find-tiles.bat
   check-tiles.bat
   verify.bat
   ```

2. **Check Docker logs:**
   ```powershell
   docker-compose logs --tail=100 valhalla
   ```

3. **Verify Docker can access D: drive:**
   - Docker Desktop → Settings → Resources → File Sharing
   - Ensure `D:` is listed and enabled

4. **Check tile structure:**
   - Tiles should be in one of the formats listed above
   - The official image auto-detects common structures
