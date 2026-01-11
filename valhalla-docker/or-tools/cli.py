#!/usr/bin/env python3
"""
CLI mode for OR-Tools VRP solver
"""
import sys
import json
import argparse
from vrp_solver import solve_vrp, get_distance_matrix, wait_for_valhalla

def main():
    parser = argparse.ArgumentParser(description="Solve VRP using OR-Tools and Valhalla")
    parser.add_argument("--num-vehicles", type=int, default=1, help="Number of vehicles")
    parser.add_argument("--depot-id", type=int, help="Depot location ID (defaults to first location)")
    parser.add_argument("--coordinates-file", type=str, help="JSON file with coordinates")
    parser.add_argument("--valhalla-url", type=str, default="http://valhalla:8002", help="Valhalla API URL")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    # Load coordinates
    if args.coordinates_file:
        with open(args.coordinates_file, 'r') as f:
            data = json.load(f)
        locations = data.get('locations', [])
    else:
        # Default test locations
        locations = [
            {"id": 1, "latitude": 45.2462012, "longitude": -74.2427412, "name": "Loc 1"},
            {"id": 2, "latitude": 45.2492513, "longitude": -74.2439336, "name": "Loc 2"},
            {"id": 3, "latitude": 45.2453229, "longitude": -74.2409535, "name": "Loc 3"}
        ]
    
    print(f"Loaded {len(locations)} locations")
    
    # Wait for Valhalla
    wait_for_valhalla(args.valhalla_url)
    
    # Get distance matrix
    print("Fetching distance matrix from Valhalla...")
    location_dicts = [{"latitude": loc["latitude"], "longitude": loc["longitude"]} for loc in locations]
    distance_matrix = get_distance_matrix(location_dicts, args.valhalla_url)
    
    if distance_matrix is None:
        print("Error: Failed to get distance matrix")
        sys.exit(1)
    
    # Determine depot index
    depot_index = 0
    if args.depot_id:
        depot_index = next((i for i, loc in enumerate(locations) if loc["id"] == args.depot_id), 0)
    
    # Solve
    print(f"\nSolving VRP with {args.num_vehicles} vehicles, depot at index {depot_index}...")
    result = solve_vrp(distance_matrix, args.num_vehicles, depot_index)
    
    if result is None:
        print("Error: No solution found")
        sys.exit(1)
    
    solution_data, routes = result
    
    # Build output
    output = {
        "status": solution_data["status"],
        "total_distance_m": solution_data.get("total_distance_m"),
        "num_locations": len(locations),
        "num_routes": len([r for r in routes if len(r) > 1]),
        "routes": []
    }
    
    for vehicle_id, route_indices in enumerate(routes):
        if len(route_indices) > 1:
            route_distance = 0
            for i in range(len(route_indices) - 1):
                route_distance += distance_matrix[route_indices[i]][route_indices[i+1]]
            
            output["routes"].append({
                "vehicle": vehicle_id + 1,
                "stops": [locations[idx] for idx in route_indices],
                "distance_m": route_distance
            })
            print(f"Route {vehicle_id + 1}: {' → '.join(str(locations[idx]['id']) for idx in route_indices)}")
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Routes saved to {args.output}")
    else:
        print("\n" + json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
