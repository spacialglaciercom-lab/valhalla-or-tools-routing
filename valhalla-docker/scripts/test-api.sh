#!/bin/bash

# Script to test Valhalla API endpoints
# This script provides example API requests for testing the Valhalla setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VALHALLA_HOST="${VALHALLA_HOST:-localhost}"
VALHALLA_PORT="${VALHALLA_PORT:-8002}"
API_BASE="http://${VALHALLA_HOST}:${VALHALLA_PORT}"

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

print_request() {
    echo -e "${BLUE}[REQUEST]${NC} $1"
}

# Function to check if service is running
check_service() {
    print_step "Checking Valhalla service status..."
    
    if curl -f -s "${API_BASE}/status" > /dev/null 2>&1; then
        print_info "Valhalla service is running"
        return 0
    else
        print_error "Valhalla service is not accessible at ${API_BASE}"
        return 1
    fi
}

# Function to get service status
test_status() {
    print_step "Testing /status endpoint..."
    print_request "GET ${API_BASE}/status"
    
    response=$(curl -s "${API_BASE}/status")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to test route endpoint
test_route() {
    local lat1=${1:-37.7749}
    local lon1=${2:--122.4194}
    local lat2=${3:-37.7849}
    local lon2=${4:--122.4094}
    local costing=${5:-auto}
    
    print_step "Testing /route endpoint..."
    print_info "From: ($lat1, $lon1) - To: ($lat2, $lon2)"
    print_info "Costing: $costing"
    
    local request_body=$(cat <<EOF
{
  "locations": [
    {"lat": $lat1, "lon": $lon1},
    {"lat": $lat2, "lon": $lon2}
  ],
  "costing": "$costing",
  "directions_options": {
    "units": "kilometers"
  }
}
EOF
)
    
    print_request "POST ${API_BASE}/route"
    echo "Request body:"
    echo "$request_body" | jq '.'
    echo ""
    
    response=$(curl -s -X POST "${API_BASE}/route" \
        -H "Content-Type: application/json" \
        -d "$request_body")
    
    echo "Response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to test isochrone endpoint
test_isochrone() {
    local lat=${1:-37.7749}
    local lon=${2:--122.4194}
    local contours=${3:-15}
    local costing=${4:-auto}
    
    print_step "Testing /isochrone endpoint..."
    print_info "Center: ($lat, $lon)"
    print_info "Contours: ${contours} minutes"
    print_info "Costing: $costing"
    
    local request_body=$(cat <<EOF
{
  "locations": [{"lat": $lat, "lon": $lon}],
  "costing": "$costing",
  "contours": [{"time": $contours}],
  "denoise": 0.2,
  "generalize": 200
}
EOF
)
    
    print_request "POST ${API_BASE}/isochrone"
    echo "Request body:"
    echo "$request_body" | jq '.'
    echo ""
    
    response=$(curl -s -X POST "${API_BASE}/isochrone" \
        -H "Content-Type: application/json" \
        -d "$request_body")
    
    echo "Response (first 500 chars):"
    echo "$response" | head -c 500
    echo "..."
    echo ""
}

# Function to test matrix endpoint
test_matrix() {
    local lat1=${1:-37.7749}
    local lon1=${2:--122.4194}
    local lat2=${3:-37.7849}
    local lon2=${4:--122.4094}
    local costing=${5:-auto}
    
    print_step "Testing /sources_to_targets endpoint..."
    print_info "Source: ($lat1, $lon1)"
    print_info "Target: ($lat2, $lon2)"
    print_info "Costing: $costing"
    
    local request_body=$(cat <<EOF
{
  "sources": [{"lat": $lat1, "lon": $lon1}],
  "targets": [{"lat": $lat2, "lon": $lon2}],
  "costing": "$costing"
}
EOF
)
    
    print_request "POST ${API_BASE}/sources_to_targets"
    echo "Request body:"
    echo "$request_body" | jq '.'
    echo ""
    
    response=$(curl -s -X POST "${API_BASE}/sources_to_targets" \
        -H "Content-Type: application/json" \
        -d "$request_body")
    
    echo "Response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to test locate endpoint
test_locate() {
    local lat=${1:-37.7749}
    local lon=${2:--122.4194}
    
    print_step "Testing /locate endpoint..."
    print_info "Location: ($lat, $lon)"
    
    print_request "GET ${API_BASE}/locate?lon=$lon&lat=$lat"
    echo ""
    
    response=$(curl -s "${API_BASE}/locate?lon=$lon&lat=$lat")
    
    echo "Response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to test optimized route
test_optimized_route() {
    print_step "Testing /optimized_route endpoint..."
    print_info "Multiple locations with optimization"
    
    local request_body=$(cat <<EOF
{
  "locations": [
    {"lat": 37.7749, "lon": -122.4194},
    {"lat": 37.7849, "lon": -122.4094},
    {"lat": 37.7949, "lon": -122.3994}
  ],
  "costing": "auto"
}
EOF
)
    
    print_request "POST ${API_BASE}/optimized_route"
    echo "Request body:"
    echo "$request_body" | jq '.'
    echo ""
    
    response=$(curl -s -X POST "${API_BASE}/optimized_route" \
        -H "Content-Type: application/json" \
        -d "$request_body")
    
    echo "Response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to run all tests
run_all_tests() {
    print_info "Running all API tests..."
    echo ""
    
    test_status
    test_locate
    test_route
    test_isochrone
    test_matrix
    test_optimized_route
    
    print_info "All tests completed!"
}

# Main function
main() {
    print_info "Valhalla API Test Script"
    print_info "========================"
    echo ""
    
    # Check if service is running
    if ! check_service; then
        exit 1
    fi
    
    echo ""
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --status              Test status endpoint"
        echo "  --locate [LAT] [LON]  Test locate endpoint"
        echo "  --route [LAT1] [LON1] [LAT2] [LON2] [COSTING]  Test route endpoint"
        echo "  --isochrone [LAT] [LON] [MINUTES] [COSTING]  Test isochrone endpoint"
        echo "  --matrix [LAT1] [LON1] [LAT2] [LON2] [COSTING]  Test matrix endpoint"
        echo "  --optimized           Test optimized route endpoint"
        echo "  --all                 Run all tests"
        echo "  --host HOST           Set Valhalla host (default: localhost)"
        echo "  --port PORT           Set Valhalla port (default: 8002)"
        echo ""
        echo "Examples:"
        echo "  $0 --all"
        echo "  $0 --route 37.7749 -122.4194 37.7849 -122.4094 auto"
        echo "  $0 --isochrone 37.7749 -122.4194 15 pedestrian"
        exit 1
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                test_status
                shift
                ;;
            --locate)
                shift
                test_locate "${1:-37.7749}" "${2:--122.4194}"
                shift 2
                ;;
            --route)
                shift
                test_route "$1" "$2" "$3" "$4" "${5:-auto}"
                shift 5
                ;;
            --isochrone)
                shift
                test_isochrone "$1" "$2" "${3:-15}" "${4:-auto}"
                shift 4
                ;;
            --matrix)
                shift
                test_matrix "$1" "$2" "$3" "$4" "${5:-auto}"
                shift 5
                ;;
            --optimized)
                test_optimized_route
                shift
                ;;
            --all)
                run_all_tests
                exit 0
                ;;
            --host)
                shift
                VALHALLA_HOST="$1"
                API_BASE="http://${VALHALLA_HOST}:${VALHALLA_PORT}"
                shift
                ;;
            --port)
                shift
                VALHALLA_PORT="$1"
                API_BASE="http://${VALHALLA_HOST}:${VALHALLA_PORT}"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Run main function
main "$@"
