# Quick Start - Windows (Fully Automated)

## Your Setup

- **Tiles Location**: `D:\valhalla_data` (automatically detected)
- **Docker Config**: `C:\Users\Space\valhalla-docker`

## Start Valhalla (1 Step - Fully Automated!)

### Option 1: Double-click `start.bat`
Just double-click the `start.bat` file - it does everything automatically!

### Option 2: Command line
```powershell
cd C:\Users\Space\valhalla-docker
docker-compose up -d
```

The service automatically:
- ✅ Detects tiles in `D:\valhalla_data`
- ✅ Configures itself
- ✅ Starts the routing service
- ✅ No manual steps needed!

## That's it! 🎉

The service should now be running on **http://localhost:8002**

## Common Commands

```powershell
# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart service
docker-compose restart

# Check if running
docker-compose ps
```

## If Docker Can't Access D: Drive

1. Open **Docker Desktop**
2. Go to **Settings** → **Resources** → **File Sharing**
3. Add **D:** to shared drives
4. Click **Apply & Restart**

## Test a Route

```powershell
curl -X POST http://localhost:8002/route `
  -H "Content-Type: application/json" `
  -d '{\"locations\":[{\"lat\":37.7749,\"lon\":-122.4194},{\"lat\":37.7849,\"lon\":-122.4094}],\"costing\":\"auto\"}'
```
