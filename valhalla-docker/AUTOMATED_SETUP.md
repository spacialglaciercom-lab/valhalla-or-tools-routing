# Fully Automated Valhalla Setup

## ✅ Zero Configuration Required

This setup is **completely automated** - it works without any manual intervention.

## What Happens Automatically

When you run `docker-compose up -d`, the system:

1. ✅ **Pulls the official Valhalla image** (no build needed)
2. ✅ **Mounts your tiles** from `D:\valhalla_data` automatically
3. ✅ **Detects existing tiles** (`.tar` file or `tiles/` directory)
4. ✅ **Auto-generates configuration** if needed
5. ✅ **Starts the routing service** on port 8002
6. ✅ **Health checks** ensure service is ready

## One Command to Start

```powershell
docker-compose up -d
```

Or double-click: **`start.bat`**

## How It Works

### Official Image
- Uses `ghcr.io/valhalla/valhalla-scripted:latest`
- Pre-built, tested, and maintained by Valhalla team
- No compilation or build steps required

### Automatic Tile Detection
The image automatically:
- Looks for `valhalla_tiles.tar` in `/custom_files`
- Or looks for `tiles/` directory in `/custom_files`
- Uses whatever it finds (your `D:\valhalla_data`)

### Auto-Configuration
- Generates `valhalla.json` automatically if missing
- Merges with your custom config if provided
- Updates paths automatically

### Environment Variables
All set to use existing tiles:
- `use_tiles_ignore_pbf=True` - Use tiles, ignore PBF files
- `force_rebuild=False` - Don't rebuild tiles
- `build_admins=False` - Skip admin building (tiles exist)
- `serve_tiles=True` - Serve the tiles

## File Structure

```
D:\valhalla_data\          ← Your tiles (automatically mounted)
├── valhalla_tiles.tar     ← OR this file
└── tiles/                 ← OR this directory

C:\Users\Space\valhalla-docker\
├── docker-compose.yml     ← Automated configuration
├── config/
│   └── valhalla.json      ← Optional custom config
├── start.bat              ← One-click startup
└── verify.bat             ← Quick status check
```

## Verification

After starting, verify it's working:

```powershell
# Quick check
.\verify.bat

# Or manually
curl http://localhost:8002/status
```

## No Manual Steps Needed

- ❌ No configuration file editing
- ❌ No environment variable setup
- ❌ No tile path configuration
- ❌ No build commands
- ❌ No manual service start

Just run `docker-compose up -d` and it works!

## Customization (Optional)

If you want to customize, create a `.env` file:

```bash
# .env (optional)
SERVER_THREADS=8
MEMORY_LIMIT=16G
VALHALLA_PORT=8002
```

But this is **completely optional** - defaults work fine.

## Troubleshooting

### Service won't start
```powershell
# Check logs
docker-compose logs

# Verify Docker can access D: drive
# Docker Desktop → Settings → Resources → File Sharing → Add D:
```

### Tiles not found
```powershell
# Verify tiles exist
dir D:\valhalla_data

# Check inside container
docker-compose exec valhalla ls -lh /custom_files/
```

## Summary

**It just works.** No configuration, no setup, no manual steps. Just start it and use it.
