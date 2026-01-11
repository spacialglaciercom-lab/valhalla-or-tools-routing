#!/bin/bash
# Bash script to test API endpoints

echo "========================================"
echo "Testing Valhalla + OR-tools APIs"
echo "========================================"
echo ""

VALHALLA_URL="http://localhost:8002"
OR_TOOLS_URL="http://localhost:5000"

# Test Valhalla Status
echo "1. Testing Valhalla status..."
if curl -f -s -m 5 "$VALHALLA_URL/status" > /dev/null 2>&1; then
    echo "   ✓ Valhalla is healthy"
    curl -s "$VALHALLA_URL/status" | python3 -m json.tool 2>/dev/null || curl -s "$VALHALLA_URL/status"
else
    echo "   ✗ Could not connect to Valhalla"
    echo "   Make sure Valhalla is running: docker compose up -d valhalla"
fi
echo ""

# Test OR-tools Health
echo "2. Testing OR-tools health..."
if curl -f -s -m 5 "$OR_TOOLS_URL/health" > /dev/null 2>&1; then
    echo "   ✓ OR-tools API is healthy"
    curl -s "$OR_TOOLS_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$OR_TOOLS_URL/health"
else
    echo "   ✗ Could not connect to OR-tools API"
    echo "   Make sure OR-tools service is running: docker compose up -d or-tools-solver"
fi
echo ""

# Test OR-tools Root
echo "3. Testing OR-tools root endpoint..."
if curl -f -s -m 5 "$OR_TOOLS_URL/" > /dev/null 2>&1; then
    echo "   ✓ OR-tools root endpoint is accessible"
    curl -s "$OR_TOOLS_URL/" | python3 -m json.tool 2>/dev/null || curl -s "$OR_TOOLS_URL/"
else
    echo "   ✗ Could not connect to OR-tools root"
fi
echo ""

# Test OR-tools VRP Solve
echo "4. Testing OR-tools VRP solve endpoint..."
TEST_PAYLOAD='{
  "locations": [
    {"id": 1, "latitude": 45.2462012, "longitude": -74.2427412, "name": "Loc 1"},
    {"id": 2, "latitude": 45.2492513, "longitude": -74.2439336, "name": "Loc 2"},
    {"id": 3, "latitude": 45.2453229, "longitude": -74.2409535, "name": "Loc 3"}
  ],
  "num_vehicles": 1,
  "depot_id": 1
}'

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$OR_TOOLS_URL/api/v1/solve" \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD" \
  -m 60)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "   ✓ VRP solve request successful"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "   ✗ VRP solve returned status code: $HTTP_CODE"
    echo "$BODY"
fi
echo ""

echo "========================================"
echo "Test Complete"
echo "========================================"
echo ""
echo "To view service logs:"
echo "  docker compose logs -f valhalla"
echo "  docker compose logs -f or-tools-solver"
echo ""
