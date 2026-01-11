#!/bin/bash

# Script to build Valhalla tiles from OSM data
# This script can be run inside the Docker container or locally

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
TILE_DIR="${TILE_DIR:-${DATA_DIR}/tiles}"
TILE_TAR="${TILE_TAR:-${DATA_DIR}/valhalla_tiles.tar}"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate OSM files
validate_osm_files() {
    local files_found=0
    
    print_step "Checking for OSM data files..."
    
    # Check for .pbf files
    for file in "${DATA_DIR}"/*.pbf; do
        if [ -f "$file" ]; then
            files_found=$((files_found + 1))
            print_info "Found OSM file: $file"
            # Check file size
            size=$(du -h "$file" | cut -f1)
            print_info "  Size: $size"
        fi
    done
    
    if [ $files_found -eq 0 ]; then
        print_error "No OSM .pbf files found in ${DATA_DIR}"
        print_info "Please download OSM data first using download-osm-data.sh"
        return 1
    fi
    
    print_info "Found $files_found OSM file(s)"
    return 0
}

# Function to create configuration if it doesn't exist
create_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_step "Creating Valhalla configuration..."
        
        # Create config directory if it doesn't exist
        mkdir -p "$(dirname "$CONFIG_FILE")"
        
        # Build config using valhalla_build_config
        if command_exists valhalla_build_config; then
            valhalla_build_config \
                --mjolnir-tile-dir "$TILE_DIR" \
                --mjolnir-tile-extract "$TILE_TAR" \
                --mjolnir-admin "${DATA_DIR}/admins/admins.sqlite" \
                --mjolnir-timezone "${DATA_DIR}/timezones/timezones.sqlite" \
                --mjolnir-concurrency "${SERVER_THREADS:-4}" \
                > "$CONFIG_FILE"
            
            print_info "Configuration created: $CONFIG_FILE"
        else
            print_error "valhalla_build_config not found. Please ensure Valhalla is installed."
            return 1
        fi
    else
        print_info "Using existing configuration: $CONFIG_FILE"
    fi
}

# Function to build admin database
build_admins() {
    if [ "${BUILD_ADMINS:-True}" != "True" ]; then
        print_info "Skipping admin database build (BUILD_ADMINS=False)"
        return 0
    fi
    
    print_step "Building admin boundaries database..."
    
    # Create admins directory
    mkdir -p "${DATA_DIR}/admins"
    
    # Collect all .pbf files
    pbf_files=""
    for file in "${DATA_DIR}"/*.pbf; do
        if [ -f "$file" ]; then
            pbf_files="${pbf_files} ${file}"
        fi
    done
    
    if [ -z "$pbf_files" ]; then
        print_error "No PBF files found for admin building"
        return 1
    fi
    
    if command_exists valhalla_build_admins; then
        valhalla_build_admins --config "$CONFIG_FILE" $pbf_files
        print_info "Admin database built successfully"
    else
        print_error "valhalla_build_admins not found"
        return 1
    fi
}

# Function to build timezone database
build_timezones() {
    if [ "${BUILD_TIME_ZONES:-True}" != "True" ]; then
        print_info "Skipping timezone database build (BUILD_TIME_ZONES=False)"
        return 0
    fi
    
    print_step "Building timezone database..."
    
    # Create timezones directory
    mkdir -p "${DATA_DIR}/timezones"
    
    if command_exists valhalla_build_timezones; then
        valhalla_build_timezones > "${DATA_DIR}/timezones/timezones.sqlite"
        print_info "Timezone database built successfully"
    else
        print_error "valhalla_build_timezones not found"
        return 1
    fi
}

# Function to build elevation data
build_elevation() {
    if [ "${BUILD_ELEVATION:-False}" != "True" ]; then
        print_info "Skipping elevation data build (BUILD_ELEVATION=False)"
        return 0
    fi
    
    print_step "Building elevation data..."
    
    # Create elevation directory
    mkdir -p "${DATA_DIR}/elevation"
    
    if command_exists valhalla_build_elevation; then
        # First build tiles, then add elevation
        print_info "Elevation will be added after initial tile build"
        return 0
    else
        print_error "valhalla_build_elevation not found"
        return 1
    fi
}

# Function to build routing tiles
build_routing_tiles() {
    print_step "Building routing tiles..."
    
    # Create tiles directory
    mkdir -p "$TILE_DIR"
    
    # Collect all .pbf files
    pbf_files=""
    for file in "${DATA_DIR}"/*.pbf; do
        if [ -f "$file" ]; then
            pbf_files="${pbf_files} ${file}"
        fi
    done
    
    if [ -z "$pbf_files" ]; then
        print_error "No PBF files found for tile building"
        return 1
    fi
    
    print_info "Building tiles from: $pbf_files"
    
    if command_exists valhalla_build_tiles; then
        # Build initial graph
        print_info "Building initial graph..."
        valhalla_build_tiles -c "$CONFIG_FILE" -e build $pbf_files
        
        # Add elevation if requested
        if [ "${BUILD_ELEVATION:-False}" == "True" ]; then
            print_info "Adding elevation data..."
            valhalla_build_elevation --from-tiles --decompress -c "$CONFIG_FILE" -v
        fi
        
        # Enhance the graph
        print_info "Enhancing graph with additional data..."
        valhalla_build_tiles -c "$CONFIG_FILE" -s enhance $pbf_files
        
        print_info "Routing tiles built successfully"
        
        # Create tar archive if requested
        if [ "${BUILD_TAR:-True}" == "True" ]; then
            print_step "Creating tile archive..."
            cd "$(dirname "$TILE_DIR")"
            tar -cf "$TILE_TAR" -C "$(basename "$TILE_DIR")" .
            print_info "Tile archive created: $TILE_TAR"
        fi
    else
        print_error "valhalla_build_tiles not found"
        return 1
    fi
}

# Main function
main() {
    print_info "Valhalla Tile Building Script"
    print_info "============================="
    echo ""
    
    # Check if running in Docker or locally
    if [ -f "/.dockerenv" ]; then
        print_info "Running inside Docker container"
    else
        print_warn "Running outside Docker - ensure Valhalla is installed locally"
    fi
    
    echo ""
    
    # Validate OSM files
    if ! validate_osm_files; then
        exit 1
    fi
    
    echo ""
    
    # Create configuration
    if ! create_config; then
        exit 1
    fi
    
    echo ""
    
    # Build admin database
    if ! build_admins; then
        print_warn "Admin database build failed, continuing..."
    fi
    
    echo ""
    
    # Build timezone database
    if ! build_timezones; then
        print_warn "Timezone database build failed, continuing..."
    fi
    
    echo ""
    
    # Build routing tiles
    if ! build_routing_tiles; then
        print_error "Tile building failed"
        exit 1
    fi
    
    echo ""
    print_info "========================================="
    print_info "Tile building completed successfully!"
    print_info "========================================="
    print_info "Tiles location: $TILE_DIR"
    if [ -f "$TILE_TAR" ]; then
        print_info "Tile archive: $TILE_TAR"
    fi
    print_info "Configuration: $CONFIG_FILE"
}

# Run main function
main "$@"
