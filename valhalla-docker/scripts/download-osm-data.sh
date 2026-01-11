#!/bin/bash

# Script to download OSM (OpenStreetMap) data for Valhalla
# This script downloads OSM data from various sources based on region selection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DATA_DIR="${DATA_DIR:-./data}"
GEOFABRIK_BASE_URL="https://download.geofabrik.de"
OSM_BASE_URL="https://planet.openstreetmap.org"

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

# Function to download file with progress
download_file() {
    local url=$1
    local output=$2
    
    print_info "Downloading: $url"
    print_info "Output: $output"
    
    if command -v wget &> /dev/null; then
        wget --progress=bar:force:noscroll -O "$output" "$url" || {
            print_error "Download failed with wget"
            return 1
        }
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$output" "$url" || {
            print_error "Download failed with curl"
            return 1
        }
    else
        print_error "Neither wget nor curl is available"
        return 1
    fi
    
    print_info "Download completed: $output"
}

# Function to download by bounding box (using BBBike extract service)
download_by_bbox() {
    local min_lon=$1
    local min_lat=$2
    local max_lon=$3
    local max_lat=$4
    local output_file="${DATA_DIR}/custom_region.osm.pbf"
    
    print_info "Downloading OSM data for bounding box:"
    print_info "  Min: ($min_lon, $min_lat)"
    print_info "  Max: ($max_lon, $max_lat)"
    
    # Using BBBike extract service
    local bbox_url="https://extract.bbbike.org/?sw_lng=${min_lon}&sw_lat=${min_lat}&ne_lng=${max_lon}&ne_lat=${max_lat}&format=osm.pbf"
    
    print_warn "BBBike extract service requires manual download"
    print_warn "Please visit: $bbox_url"
    print_warn "Or use osmium tool to extract from planet file"
}

# Function to download by region name (Geofabrik)
download_region() {
    local region=$1
    local output_file="${DATA_DIR}/${region}-latest.osm.pbf"
    
    # Check if file already exists
    if [ -f "$output_file" ]; then
        print_warn "File already exists: $output_file"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping download"
            return 0
        fi
    fi
    
    # Construct URL
    local url="${GEOFABRIK_BASE_URL}/${region}-latest.osm.pbf"
    
    # Create data directory if it doesn't exist
    mkdir -p "$DATA_DIR"
    
    # Download the file
    download_file "$url" "$output_file"
    
    print_info "OSM data downloaded successfully: $output_file"
}

# Function to list available regions
list_regions() {
    print_info "Available regions from Geofabrik:"
    echo ""
    echo "Continents:"
    echo "  africa, antarctica, asia, australia-oceania, central-america,"
    echo "  europe, north-america, south-america"
    echo ""
    echo "Countries (examples):"
    echo "  albania, andorra, austria, belgium, bulgaria, croatia,"
    echo "  czech-republic, denmark, estonia, finland, france, germany,"
    echo "  greece, hungary, iceland, ireland, italy, latvia, liechtenstein,"
    echo "  lithuania, luxembourg, malta, netherlands, norway, poland,"
    echo "  portugal, romania, slovakia, slovenia, spain, sweden,"
    echo "  switzerland, united-kingdom"
    echo ""
    echo "US States (examples):"
    echo "  alabama, alaska, arizona, arkansas, california, colorado,"
    echo "  connecticut, delaware, florida, georgia, hawaii, idaho,"
    echo "  illinois, indiana, iowa, kansas, kentucky, louisiana, maine,"
    echo "  maryland, massachusetts, michigan, minnesota, mississippi,"
    echo "  missouri, montana, nebraska, nevada, new-hampshire,"
    echo "  new-jersey, new-mexico, new-york, north-carolina,"
    echo "  north-dakota, ohio, oklahoma, oregon, pennsylvania,"
    echo "  rhode-island, south-carolina, south-dakota, tennessee, texas,"
    echo "  utah, vermont, virginia, washington, west-virginia,"
    echo "  wisconsin, wyoming, district-of-columbia"
    echo ""
    echo "For full list, visit: ${GEOFABRIK_BASE_URL}"
}

# Main script
main() {
    print_info "OSM Data Download Script for Valhalla"
    print_info "====================================="
    echo ""
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --region REGION_NAME     Download by region name (e.g., 'europe/germany')"
        echo "  --bbox MIN_LON MIN_LAT MAX_LON MAX_LAT  Download by bounding box"
        echo "  --url URL                Download from custom URL"
        echo "  --list                   List available regions"
        echo "  --data-dir DIR           Set data directory (default: ./data)"
        echo ""
        echo "Examples:"
        echo "  $0 --region europe/germany"
        echo "  $0 --region north-america/us/california"
        echo "  $0 --url https://download.geofabrik.de/europe/andorra-latest.osm.pbf"
        echo "  $0 --bbox -122.5 37.7 -122.3 37.8  # San Francisco Bay Area"
        exit 1
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --region)
                shift
                if [ -z "$1" ]; then
                    print_error "Region name required"
                    exit 1
                fi
                download_region "$1"
                shift
                ;;
            --bbox)
                shift
                if [ $# -lt 4 ]; then
                    print_error "Bounding box requires 4 coordinates"
                    exit 1
                fi
                download_by_bbox "$1" "$2" "$3" "$4"
                shift 4
                ;;
            --url)
                shift
                if [ -z "$1" ]; then
                    print_error "URL required"
                    exit 1
                fi
                filename=$(basename "$1")
                output_file="${DATA_DIR}/${filename}"
                mkdir -p "$DATA_DIR"
                download_file "$1" "$output_file"
                shift
                ;;
            --list)
                list_regions
                exit 0
                ;;
            --data-dir)
                shift
                DATA_DIR="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_info "Download process completed!"
}

# Run main function
main "$@"
