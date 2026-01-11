#!/bin/bash

# Script to start Valhalla service
# This script handles the startup sequence for Valhalla

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATA_DIR="${DATA_DIR:-/custom_files}"
CONFIG_FILE="${CONFIG_FILE:-${DATA_DIR}/config/valhalla.json}"
VALHALLA_PORT="${VALHALLA_PORT:-8002}"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if Valhalla is already running
check_running() {
    if pgrep -f "valhalla_service" > /dev/null; then
        return 0
    fi
    return 1
}

# Function to wait for service to be ready
wait_for_service() {
    local max_attempts=30
    local attempt=0
    
    print_info "Waiting for Valhalla service to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "http://localhost:${VALHALLA_PORT}/status" > /dev/null 2>&1; then
            print_info "Valhalla service is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_error "Valhalla service did not become ready in time"
    return 1
}

# Function to validate configuration
validate_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        print_info "Please ensure valhalla.json exists in the config directory"
        return 1
    fi
    
    # Validate JSON syntax
    if command -v jq &> /dev/null; then
        if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
            print_error "Invalid JSON in configuration file"
            return 1
        fi
    fi
    
    print_info "Configuration file validated: $CONFIG_FILE"
    return 0
}

# Function to check for tiles
check_tiles() {
    local tile_dir=$(jq -r '.mjolnir.tile_dir' "$CONFIG_FILE" 2>/dev/null || echo "${DATA_DIR}/tiles")
    local tile_extract=$(jq -r '.mjolnir.tile_extract' "$CONFIG_FILE" 2>/dev/null || echo "${DATA_DIR}/valhalla_tiles.tar")
    
    if [ -f "$tile_extract" ]; then
        print_info "Found tile archive: $tile_extract"
        return 0
    elif [ -d "$tile_dir" ] && [ "$(ls -A "$tile_dir" 2>/dev/null)" ]; then
        print_info "Found tile directory: $tile_dir"
        return 0
    else
        print_warn "No tiles found. Valhalla will start but routing may not work."
        print_warn "Please build tiles first using build-tiles.sh"
        return 1
    fi
}

# Main function
main() {
    print_info "Valhalla Service Startup Script"
    print_info "==============================="
    echo ""
    
    # Check if already running
    if check_running; then
        print_warn "Valhalla service appears to be already running"
        read -p "Stop and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Stopping existing service..."
            pkill -f "valhalla_service" || true
            sleep 2
        else
            print_info "Exiting. Service is already running."
            exit 0
        fi
    fi
    
    # Validate configuration
    if ! validate_config; then
        exit 1
    fi
    
    echo ""
    
    # Check for tiles (non-fatal)
    check_tiles
    
    echo ""
    
    # Start Valhalla service
    print_step "Starting Valhalla service..."
    print_info "Configuration: $CONFIG_FILE"
    print_info "Port: $VALHALLA_PORT"
    echo ""
    
    # Start in background and capture PID
    valhalla_service "$CONFIG_FILE" &
    VALHALLA_PID=$!
    
    # Wait a moment for process to start
    sleep 2
    
    # Check if process is still running
    if ! kill -0 $VALHALLA_PID 2>/dev/null; then
        print_error "Valhalla service failed to start"
        exit 1
    fi
    
    print_info "Valhalla service started (PID: $VALHALLA_PID)"
    
    # Wait for service to be ready
    if wait_for_service; then
        echo ""
        print_info "========================================="
        print_info "Valhalla service is running!"
        print_info "========================================="
        print_info "API endpoint: http://localhost:${VALHALLA_PORT}"
        print_info "Status endpoint: http://localhost:${VALHALLA_PORT}/status"
        print_info "To stop the service, use: kill $VALHALLA_PID"
        echo ""
        
        # Keep script running and handle signals
        trap "print_info 'Shutting down Valhalla service...'; kill $VALHALLA_PID; exit" SIGTERM SIGINT
        
        # Wait for process
        wait $VALHALLA_PID
    else
        print_error "Service startup failed"
        kill $VALHALLA_PID 2>/dev/null || true
        exit 1
    fi
}

# Run main function
main "$@"
