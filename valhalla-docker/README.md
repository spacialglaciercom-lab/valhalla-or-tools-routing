# Valhalla Routing Engine - Docker Setup

Complete Docker configuration for running Valhalla routing engine with existing tiles.

## Overview

This setup provides a production-ready Docker environment for Valhalla routing engine. The configuration assumes you already have Valhalla tiles downloaded and ready to use.

## Prerequisites

- Docker and Docker Compose installed
- Existing Valhalla tiles (`.tar` file or tile directory)
- `valhalla.json` configuration file

## Quick Start

### 1. Prepare Your Data

Your Valhalla tiles should be in `D:\valhalla_data`:

```bash
# Option 1: Tile archive
D:\valhalla_data\valhalla_tiles.tar

# Option 2: Tile directory
D:\valhalla_data\tiles\
```

The Docker configuration is set to mount `D:\valhalla_data` automatically.

### 2. Configure Environment (Optional)

Create a `.env` file to customize settings:

```bash
# Port configuration
VALHALLA_PORT=8002

# Performance settings
SERVER_THREADS=4
CPU_LIMIT=4.0
MEMORY_LIMIT=8G

# Build options (set to False if tiles already exist)
FORCE_REBUILD=False
USE_TILES_IGNORE_PBF=True
```

### 3. Start the Service

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
curl http://localhost:8002/status
```

### 4. Test the API

```bash
# Run test script
./scripts/test-api.sh --all

# Or test individual endpoints
./scripts/test-api.sh --status
./scripts/test-api.sh --route 37.7749 -122.4194 37.7849 -122.4094 auto
```

## Directory Structure

```
valhalla-docker/
├── Dockerfile                 # Multi-stage build for Valhalla
├── docker-compose.yml         # Service orchestration
├── config/
│   └── valhalla.json         # Valhalla configuration
├── scripts/
│   ├── build-tiles.sh        # Build tiles from OSM data (if needed)
│   ├── start-valhalla.sh     # Start Valhalla service
│   └── test-api.sh           # Test API endpoints
└── README.md                 # This file

D:\valhalla_data\              # Your tiles location (mounted as volume)
├── tiles/                     # Tile directory (if not using .tar)
├── valhalla_tiles.tar         # Tile archive (alternative)
├── admins/                    # Admin boundaries (optional)
├── timezones/                 # Timezone data (optional)
└── elevation/                 # Elevation data (optional)
```

## Configuration

### valhalla.json

The main configuration file is located at `config/valhalla.json`. Key settings:

- **mjolnir.tile_dir**: Directory containing routing tiles
- **mjolnir.tile_extract**: Path to tile archive (`.tar` file)
- **mjolnir.concurrency**: Number of worker threads
- **httpd.service.listen**: API listening address and port

### Environment Variables

Configure via `.env` file or `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VALHALLA_PORT` | 8002 | API port |
| `SERVER_THREADS` | 4 | Worker threads |
| `USE_TILES_IGNORE_PBF` | True | Use existing tiles, ignore PBF files |
| `FORCE_REBUILD` | False | Force tile rebuild |
| `BUILD_ADMINS` | True | Build admin boundaries |
| `BUILD_TIME_ZONES` | True | Build timezone data |
| `BUILD_ELEVATION` | False | Build elevation data |
| `CPU_LIMIT` | 4.0 | CPU limit for container |
| `MEMORY_LIMIT` | 8G | Memory limit for container |

## API Endpoints

### Status
```bash
curl http://localhost:8002/status
```

### Route
```bash
curl -X POST http://localhost:8002/route \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [
      {"lat": 37.7749, "lon": -122.4194},
      {"lat": 37.7849, "lon": -122.4094}
    ],
    "costing": "auto"
  }'
```

### Isochrone
```bash
curl -X POST http://localhost:8002/isochrone \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [{"lat": 37.7749, "lon": -122.4194}],
    "costing": "auto",
    "contours": [{"time": 15}]
  }'
```

### Matrix (Sources to Targets)
```bash
curl -X POST http://localhost:8002/sources_to_targets \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"lat": 37.7749, "lon": -122.4194}],
    "targets": [{"lat": 37.7849, "lon": -122.4094}],
    "costing": "auto"
  }'
```

### Locate
```bash
curl "http://localhost:8002/locate?lon=-122.4194&lat=37.7749"
```

## Routing Profiles

Valhalla supports multiple routing profiles:

- **auto**: Car routing (default)
- **bicycle**: Bicycle routing
- **pedestrian**: Walking routing
- **bus**: Public transit routing
- **taxi**: Taxi routing with different restrictions

Specify in requests:
```json
{
  "costing": "bicycle",
  "costing_options": {
    "bicycle": {
      "bicycle_type": "Road"
    }
  }
}
```

## Performance Optimization

### Memory Settings

Adjust based on your tile size:

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 16G  # Increase for large regions
    reservations:
      memory: 8G
```

### Thread Configuration

```yaml
environment:
  - SERVER_THREADS=8  # Match your CPU cores
```

### Cache Size

In `valhalla.json`:
```json
{
  "mjolnir": {
    "max_cache_size": 2000000000  # 2GB cache
  }
}
```

## Troubleshooting

### Service won't start

1. Check logs:
   ```bash
   docker-compose logs valhalla
   ```

2. Verify tiles exist:
   ```bash
   # Windows PowerShell
   dir D:\valhalla_data\valhalla_tiles.tar
   # or
   dir D:\valhalla_data\tiles\
   
   # Or check inside container
   docker-compose exec valhalla ls -lh /custom_files/
   ```

3. Check configuration:
   ```bash
   docker-compose exec valhalla cat /custom_files/config/valhalla.json
   ```

### API returns errors

1. Check service status:
   ```bash
   curl http://localhost:8002/status
   ```

2. Verify tiles are loaded:
   ```bash
   docker-compose exec valhalla ls -lh /custom_files/tiles/
   ```

3. Check for errors in logs:
   ```bash
   docker-compose logs --tail=100 valhalla
   ```

### Performance issues

1. Increase memory limits
2. Adjust `SERVER_THREADS` to match CPU cores
3. Increase `max_cache_size` in configuration
4. Use tile archive (`.tar`) instead of directory for faster loading

## Building from Source

If you need to build Valhalla from source:

1. Update `Dockerfile` to clone from GitHub or copy source
2. Build the image:
   ```bash
   docker-compose build --no-cache
   ```

## Health Checks

The container includes automatic health checks:

```bash
# Check health status
docker-compose ps

# Manual health check
curl http://localhost:8002/status
```

## Stopping the Service

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Additional Resources

- [Valhalla Documentation](https://github.com/valhalla/valhalla)
- [Valhalla API Documentation](https://valhalla.github.io/valhalla/api/)
- [OpenStreetMap Data](https://www.openstreetmap.org/)

## License

This Docker setup follows the same license as Valhalla (MIT License).
