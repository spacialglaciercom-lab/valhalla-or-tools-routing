# Windows Setup Guide

## Tile Location

Your Valhalla tiles are located at: **`D:\valhalla_data`**

The Docker configuration automatically mounts this directory to the container.

## Directory Structure

Your `D:\valhalla_data` folder should contain one of the following:

### Option 1: Tile Archive
```
D:\valhalla_data\
└── valhalla_tiles.tar
```

### Option 2: Tile Directory
```
D:\valhalla_data\
└── tiles\
    ├── 0\
    ├── 1\
    ├── 2\
    └── ... (tile files)
```

## Starting the Service

1. **Navigate to the valhalla-docker directory:**
   ```powershell
   cd C:\Users\Space\valhalla-docker
   ```

2. **Start Docker Desktop** (if not already running)

3. **Start the service:**
   ```powershell
   docker-compose up -d
   ```

4. **Check status:**
   ```powershell
   curl http://localhost:8002/status
   ```

## Verifying Tiles

To verify your tiles are accessible:

```powershell
# Check if tiles exist
dir D:\valhalla_data

# Check inside container
docker-compose exec valhalla ls -lh /custom_files/
```

## Troubleshooting

### Docker can't access D: drive

If Docker Desktop can't access the D: drive:

1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Add `D:\` to the shared drives
4. Click "Apply & Restart"

### Path Format

The docker-compose.yml uses forward slashes (`D:/valhalla_data`) which works on Windows with Docker Desktop. If you encounter issues, you can also try:

- `D:\valhalla_data` (backslashes)
- `/d/valhalla_data` (WSL-style path)

### Permission Issues

If you get permission errors:

1. Ensure Docker Desktop has access to D: drive (see above)
2. Check folder permissions on `D:\valhalla_data`
3. Run Docker Desktop as Administrator if needed

## Testing

Once the service is running:

```powershell
# Test status endpoint
curl http://localhost:8002/status

# Test route (example coordinates)
curl -X POST http://localhost:8002/route `
  -H "Content-Type: application/json" `
  -d '{\"locations\":[{\"lat\":37.7749,\"lon\":-122.4194},{\"lat\":37.7849,\"lon\":-122.4094}],\"costing\":\"auto\"}'
```

## Notes

- The tiles are mounted read-only by default (you can modify this in docker-compose.yml if needed)
- All paths in the container use `/custom_files/` which maps to `D:\valhalla_data`
- The configuration file is in `C:\Users\Space\valhalla-docker\config\valhalla.json`
