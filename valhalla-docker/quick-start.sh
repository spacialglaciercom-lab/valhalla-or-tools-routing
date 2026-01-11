#!/bin/bash

# Quick start script for Valhalla Docker setup
# This script helps you get started quickly with existing tiles

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Valhalla Docker Quick Start${NC}"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check for tiles
TILES_FOUND=false
if [ -f "data/valhalla_tiles.tar" ]; then
    echo -e "${GREEN}✓ Found tile archive: data/valhalla_tiles.tar${NC}"
    TILES_FOUND=true
elif [ -d "data/tiles" ] && [ "$(ls -A data/tiles 2>/dev/null)" ]; then
    echo -e "${GREEN}✓ Found tile directory: data/tiles/${NC}"
    TILES_FOUND=true
fi

if [ "$TILES_FOUND" = false ]; then
    echo -e "${YELLOW}⚠ Warning: No tiles found in data/ directory${NC}"
    echo "Please ensure you have either:"
    echo "  - data/valhalla_tiles.tar, or"
    echo "  - data/tiles/ directory with tile files"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for config
if [ ! -f "config/valhalla.json" ]; then
    echo -e "${YELLOW}⚠ Warning: config/valhalla.json not found${NC}"
    echo "Creating default config directory..."
    mkdir -p config
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    fi
fi

echo ""
echo "Starting Valhalla service..."
echo ""

# Start the service
docker-compose up -d

echo ""
echo -e "${GREEN}Valhalla service is starting...${NC}"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To check status:"
echo "  curl http://localhost:8002/status"
echo ""
echo "To test the API:"
echo "  ./scripts/test-api.sh --all"
echo ""
echo "To stop the service:"
echo "  docker-compose down"
echo ""
