# PowerShell script to test API endpoints

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Valhalla + OR-tools APIs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$valhallaUrl = "http://localhost:8002"
$orToolsUrl = "http://localhost:5000"

# Test Valhalla Status
Write-Host "1. Testing Valhalla status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$valhallaUrl/status" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Valhalla is healthy" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ Valhalla returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Could not connect to Valhalla: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure Valhalla is running: docker compose up -d valhalla" -ForegroundColor Yellow
}
Write-Host ""

# Test OR-tools Health
Write-Host "2. Testing OR-tools health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$orToolsUrl/health" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ OR-tools API is healthy" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ OR-tools API returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Could not connect to OR-tools API: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure OR-tools service is running: docker compose up -d or-tools-solver" -ForegroundColor Yellow
}
Write-Host ""

# Test OR-tools Root
Write-Host "3. Testing OR-tools root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$orToolsUrl/" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ OR-tools root endpoint is accessible" -ForegroundColor Green
        $json = $response.Content | ConvertFrom-Json
        Write-Host "   Name: $($json.name)" -ForegroundColor Gray
        Write-Host "   Version: $($json.version)" -ForegroundColor Gray
        Write-Host "   Valhalla URL: $($json.valhalla_url)" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ OR-tools root endpoint returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Could not connect to OR-tools root: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test OR-tools VRP Solve
Write-Host "4. Testing OR-tools VRP solve endpoint..." -ForegroundColor Yellow
$testPayload = @{
    locations = @(
        @{id = 1; latitude = 45.2462012; longitude = -74.2427412; name = "Loc 1"},
        @{id = 2; latitude = 45.2492513; longitude = -74.2439336; name = "Loc 2"},
        @{id = 3; latitude = 45.2453229; longitude = -74.2409535; name = "Loc 3"}
    )
    num_vehicles = 1
    depot_id = 1
} | ConvertTo-Json -Depth 10

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    $response = Invoke-WebRequest -Uri "$orToolsUrl/api/v1/solve" -Method POST -Body $testPayload -Headers $headers -UseBasicParsing -TimeoutSec 60
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ VRP solve request successful" -ForegroundColor Green
        $result = $response.Content | ConvertFrom-Json
        Write-Host "   Status: $($result.status)" -ForegroundColor Gray
        Write-Host "   Total distance: $($result.total_distance_m) meters" -ForegroundColor Gray
        Write-Host "   Number of routes: $($result.num_routes)" -ForegroundColor Gray
        Write-Host "   Vehicles used: $($result.num_vehicles_used)" -ForegroundColor Gray
        if ($result.routes) {
            foreach ($route in $result.routes) {
                Write-Host "   Route $($route.vehicle): $($route.distance_m) meters, $($route.stops.Count) stops" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   ✗ VRP solve returned status code: $($response.StatusCode)" -ForegroundColor Red
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ VRP solve request failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view service logs:" -ForegroundColor Yellow
Write-Host "  docker compose logs -f valhalla" -ForegroundColor White
Write-Host "  docker compose logs -f or-tools-solver" -ForegroundColor White
Write-Host ""
