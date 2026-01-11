#!/usr/bin/env python3
"""
Example client for OR-Tools VRP Solver API
"""
import requests
import json

API_URL = "http://localhost:5000"

def solve_vrp_example():
    """Example: Solve VRP with sample locations"""
    
    # Sample locations
    locations = [
        {"id": 1, "latitude": 45.2462012, "longitude": -74.2427412, "name": "Loc 1"},
        {"id": 2, "latitude": 45.2492513, "longitude": -74.2439336, "name": "Loc 2"},
        {"id": 3, "latitude": 45.2453229, "longitude": -74.2409535, "name": "Loc 3"}
    ]
    
    # Request payload
    payload = {
        "locations": locations,
        "num_vehicles": 1,
        "depot_id": 1
    }
    
    try:
        # Check health first
        print("Checking API health...")
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"API health check failed: {health_response.status_code}")
            return
        print("✓ API is healthy")
        
        # Solve VRP
        print(f"\nSolving VRP for {len(locations)} locations with 1 vehicle...")
        response = requests.post(
            f"{API_URL}/api/v1/solve",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Solution found!")
            print(f"\nTotal distance: {result.get('total_distance_m', 0)} meters")
            print(f"Number of routes: {result.get('num_routes', 0)}")
            print(f"Vehicles used: {result.get('num_vehicles_used', 0)}")
            
            print("\nRoutes:")
            for route in result.get('routes', []):
                print(f"\n  Vehicle {route['vehicle']}:")
                print(f"    Distance: {route['distance_m']} meters")
                print(f"    Stops ({len(route['stops'])}):")
                for stop in route['stops']:
                    name = stop.get('name', f"Loc {stop['id']}")
                    print(f"      - {name} (ID: {stop['id']}) at ({stop['latitude']}, {stop['longitude']})")
            
            # Pretty print full result
            print("\n" + "="*60)
            print("Full JSON Response:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {API_URL}")
        print("Make sure the OR-tools solver service is running:")
        print("  docker compose up -d or-tools-solver")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_vrp_example()
