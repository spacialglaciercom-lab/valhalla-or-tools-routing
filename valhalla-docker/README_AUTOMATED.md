# Valhalla Docker - Fully Automated Setup

## 🚀 Zero-Configuration Startup

This setup is **fully automated** - just run one command and it works!

## Quick Start (One Command)

### Windows:
```powershell
docker-compose up -d
```

Or double-click: **`start.bat`**

That's it! The service will:
- ✅ Automatically use tiles from `D:\valhalla_data`
- ✅ Auto-configure everything
- ✅ Start the routing service
- ✅ Be available at `http://localhost:8002`

## How It Works

The setup uses the **official Valhalla Docker image** which:
1. Automatically detects tiles in `/custom_files` (your `D:\valhalla_data`)
2. Auto-generates configuration if needed
3. Uses existing tiles without rebuilding
4. Starts the service automatically

## Your Setup

- **Tiles**: `D:\valhalla_data` (automatically mounted)
- **Config**: `C:\Users\Space\valhalla-docker\config\valhalla.json` (optional, auto-merged)
- **Port**: `8002` (default)

## Verify It's Working

```powershell
# Check status
curl http://localhost:8002/status

# Test a route
curl -X POST http://localhost:8002/route -H "Content-Type: application/json" -d "{\"locations\":[{\"lat\":37.7749,\"lon\":-122.4194},{\"lat\":37.7849,\"lon\":-122.4094}],\"costing\":\"auto\"}"
```

## Common Commands

```powershell
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

## Troubleshooting

### Docker can't access D: drive
1. Docker Desktop → Settings → Resources → File Sharing
2. Add `D:` to shared drives
3. Click "Apply & Restart"

### Service won't start
```powershell
# Check logs
docker-compose logs

# Verify tiles exist
dir D:\valhalla_data
```

## That's All!

No manual configuration needed. The official image handles everything automatically.
