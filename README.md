# Valhalla + OR-tools Routing System

A comprehensive routing system combining Valhalla routing engine, OR-tools VRP solver, and trash collection route generation with a Streamlit web interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## Features

- **Valhalla Routing Engine** - High-performance routing and distance matrix calculations
- **OR-tools VRP Solver** - Vehicle Routing Problem optimization with multiple vehicles
- **Trash Route Generator** - Optimized trash collection routes from OSM data
- **Streamlit Web Interface** - User-friendly web UI for all services
- **Docker Integration** - Complete containerized setup
- **Fast PBF Parsing** - Using pyrosm for fast OSM PBF file processing

## Architecture

The system consists of three main Docker services:

- **Valhalla** (Port 8002) - Routing engine service
- **OR-tools Solver** (Port 5000) - VRP optimization API
- **Trash Route API** (Port 8003) - Route generation API

See [ARCHITECTURE.md](valhalla-docker/ARCHITECTURE.md) for detailed architecture documentation.

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- 10GB free disk space
- Internet connection

### 1. Start Services

```bash
cd valhalla-docker
docker compose up -d
```

Wait for services to be ready (first run may take 10-30 minutes for Valhalla to build tiles).

### 2. Check Service Status

```bash
# Check Valhalla
curl http://localhost:8002/status

# Check OR-tools API
curl http://localhost:5000/health

# Check Trash Route API
curl http://localhost:8003/health
```

### 3. Launch Streamlit Interface

```bash
cd valhalla-docker
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

The interface will be available at `http://localhost:8501`

### 4. Or Use the APIs Directly

See [QUICK_START.md](valhalla-docker/QUICK_START.md) for API usage examples.

## Installation

### Docker Services

All services run in Docker containers. See [valhalla-docker/QUICK_START.md](valhalla-docker/QUICK_START.md) for detailed setup instructions.

### Streamlit Interface (Optional)

```bash
cd valhalla-docker
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

## Usage

### Streamlit Web Interface

The Streamlit interface provides:

1. **Dashboard** - Service status and overview
2. **VRP Solver** - Solve vehicle routing problems
   - Input locations manually or via JSON
   - Configure number of vehicles and depot
   - View optimized routes and download results
3. **Trash Route Generator** - Generate routes from OSM files
   - Upload OSM files (XML or PBF)
   - Generate optimized routes
   - Download GPX files and reports

### VRP Solver API

```bash
curl -X POST http://localhost:5000/api/v1/solve \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [
      {"id": 1, "latitude": 45.2462012, "longitude": -74.2427412, "name": "Loc 1"},
      {"id": 2, "latitude": 45.2492513, "longitude": -74.2439336, "name": "Loc 2"}
    ],
    "num_vehicles": 1,
    "depot_id": 1
  }'
```

### Trash Route Generator API

```bash
# Upload OSM file
curl -X POST http://localhost:8003/upload \
  -F "file=@area.osm"

# Generate route (use job_id from upload response)
curl -X POST http://localhost:8003/generate \
  -H "Content-Type: application/json" \
  -d '{"job_id": "your-job-id"}'

# Check status
curl http://localhost:8003/status/your-job-id

# Download results
curl http://localhost:8003/download/your-job-id
```

See [valhalla-docker/README.md](valhalla-docker/README.md) for detailed API documentation.

## Project Structure

```
.
├── README.md                 # This file
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
├── valhalla-docker/         # Main Docker setup
│   ├── docker-compose.yml   # Service orchestration
│   ├── streamlit_app.py     # Streamlit web interface
│   ├── QUICK_START.md       # Quick start guide
│   ├── ARCHITECTURE.md      # Architecture documentation
│   ├── or-tools/            # OR-tools service
│   │   ├── app.py           # FastAPI server
│   │   ├── vrp_solver.py    # VRP solver implementation
│   │   └── client_example.py # Example client
│   ├── scripts/             # Utility scripts
│   └── config/              # Configuration files
├── backend/
│   └── trash-route-api/     # Trash route generation API
│       ├── app/             # FastAPI application
│       └── Dockerfile       # Container definition
├── src/
│   └── route_generator/     # Route generation logic
│       ├── osm_parser.py    # OSM file parsing (pyrosm)
│       ├── graph_builder.py # Network graph construction
│       └── ...
└── tests/                   # Test suite
```

## Technology Stack

### Routing & Optimization
- **Valhalla** - C++ routing engine
- **OR-tools** - Google's optimization library
- **NetworkX** - Python graph library

### Data Processing
- **Pyrosm** - Fast PBF parsing (Cython-based)
- **Geopandas** - GeoDataFrame operations
- **GPXpy** - GPX file generation

### APIs & Services
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Streamlit** - Web interface
- **WebSockets** - Real-time updates

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Service orchestration

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Local Development

For local development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r backend/trash-route-api/requirements.txt
pip install -r valhalla-docker/requirements-streamlit.txt

# Run Streamlit (requires services to be running)
cd valhalla-docker
streamlit run streamlit_app.py
```

### Building Docker Images

```bash
cd valhalla-docker
docker compose build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Documentation

- [Quick Start Guide](valhalla-docker/QUICK_START.md) - Get started in 5 minutes
- [Architecture Documentation](valhalla-docker/ARCHITECTURE.md) - System architecture
- [API Documentation](valhalla-docker/README.md) - Detailed API reference

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# Check ports are free
netstat -ano | findstr :8002
netstat -ano | findstr :5000
netstat -ano | findstr :8003
```

### Valhalla taking too long

- First run downloads ~5GB of map data
- Check internet connection
- Monitor progress: `docker compose logs -f valhalla`

### API errors

```bash
# Check service logs
docker compose logs or-tools-solver
docker compose logs trash-route-api

# Verify services are healthy
curl http://localhost:8002/status
curl http://localhost:5000/health
curl http://localhost:8003/health
```

See [valhalla-docker/TROUBLESHOOTING.md](valhalla-docker/TROUBLESHOOTING.md) for more troubleshooting tips.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Valhalla](https://github.com/valhalla/valhalla) - Routing engine
- [OR-tools](https://github.com/google/or-tools) - Optimization library
- [Pyrosm](https://github.com/pyrosm/pyrosm) - Fast OSM parsing
- [Streamlit](https://streamlit.io/) - Web framework
