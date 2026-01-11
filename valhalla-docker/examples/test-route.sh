#!/bin/bash

# Simple script to test a route request
# Usage: ./test-route.sh [lat1] [lon1] [lat2] [lon2] [costing]

VALHALLA_HOST="${VALHALLA_HOST:-localhost}"
VALHALLA_PORT="${VALHALLA_PORT:-8002}"

LAT1=${1:-37.7749}
LON1=${2:--122.4194}
LAT2=${3:-37.7849}
LON2=${4:--122.4094}
COSTING=${5:-auto}

echo "Testing route from ($LAT1, $LON1) to ($LAT2, $LON2) using $COSTING costing"
echo ""

curl -X POST "http://${VALHALLA_HOST}:${VALHALLA_PORT}/route" \
  -H "Content-Type: application/json" \
  -d "{
    \"locations\": [
      {\"lat\": $LAT1, \"lon\": $LON1},
      {\"lat\": $LAT2, \"lon\": $LON2}
    ],
    \"costing\": \"$COSTING\",
    \"directions_options\": {
      \"units\": \"kilometers\"
    }
  }" | jq '.'
