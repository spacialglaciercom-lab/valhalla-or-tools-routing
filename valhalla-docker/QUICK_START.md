# Quick Start Guide

Get the Valhalla + OR-tools routing system running in 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- 10GB free disk space
- Internet connection

## Step 1: Fix Permissions (Recommended)

**Valhalla runs as UID 59999:GID 59999 (non-root user)**

```bash
# Linux/Mac
chmod +x fix-permissions.sh
./fix-permissions.sh

# Windows PowerShell
.\fix-permissions.ps1
```

## Step 2: Start Services

```bash
# Start all services
docker compose up -d

# Watch Valhalla build progress (first run takes 10-30 minutes)
docker compose logs -f valhalla
```

## Step 3: Wait for Services

Wait until you see:
```
valhalla-routing  | Server is listening on port 8002
```

Then check health:
```bash
# Check Valhalla
curl http://localhost:8002/status

# Check API
curl http://localhost:5000/health
```

## Step 4: Test the API

**PowerShell:**
```powershell
.\test-api.ps1
```

**Bash:**
```bash
# Make executable
chmod +x test-api.sh
./test-api.sh
```

## Step 5: Solve VRP

### Using REST API

```bash
curl -X POST http://localhost:5000/api/v1/solve \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "locations": [
    {"id": 1, "latitude": 45.2462012, "longitude": -74.2427412, "name": "Loc 1"},
    {"id": 2, "latitude": 45.2492513, "longitude": -74.2439336, "name": "Loc 2"},
    {"id": 3, "latitude": 45.2453229, "longitude": -74.2409535, "name": "Loc 3"}
  ],
  "num_vehicles": 1,
  "depot_id": 1
}
EOF
```

### Using Python Client

```bash
cd or-tools
python client_example.py
```

### Using CLI Solver

```bash
# Run CLI solver directly
docker compose run --rm -e MODE=solver or-tools-solver \
  python cli.py --num-vehicles 1
```

## Common Commands

```bash
# View all logs
docker compose logs -f

# Restart a service
docker compose restart or-tools-solver

# Stop all services
docker compose down

# Remove everything (including map tiles)
docker compose down -v
```

## Next Steps

- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- See [README.md](README.md) for detailed documentation
- See API examples in `or-tools/client_example.py`

## Troubleshooting

**Services won't start:**
```bash
# Check Docker is running
docker ps

# Check ports are free
netstat -ano | findstr :8002
netstat -ano | findstr :5000
```

**Valhalla taking too long:**
- First run downloads ~5GB of map data
- Check internet connection
- Monitor progress: `docker compose logs -f valhalla`

**API errors:**
```bash
# Check API logs
docker compose logs or-tools-solver

# Verify Valhalla is healthy
curl http://localhost:8002/status
```
