#!/usr/bin/env python3
"""
OR-Tools VRP Solver with Valhalla integration
"""
import json
import requests
import time
from typing import List, Dict, Optional, Tuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def get_distance_matrix(locations: List[Dict], valhalla_url: str = "http://valhalla:8002") -> Optional[List[List[int]]]:
    """
    Get distance matrix from Valhalla routing engine.
    
    Args:
        locations: List of location dicts with 'latitude' and 'longitude' keys
        valhalla_url: Base URL for Valhalla API
    
    Returns:
        Distance matrix as list of lists (distances in meters), or None on error
    """
    coords = [[loc['latitude'], loc['longitude']] for loc in locations]
    
    try:
        # Valhalla sources_to_targets API format
        response = requests.post(
            f'{valhalla_url}/sources_to_targets',
            json={
                "sources": coords,
                "targets": coords,
                "costing": "auto"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'sources_to_targets' in result:
                # Extract distances (in meters) from Valhalla response
                distances = []
                for row in result['sources_to_targets']:
                    distance_row = []
                    for cell in row:
                        # Valhalla returns distance in meters
                        distance_m = int(cell.get('distance', 0))
                        distance_row.append(distance_m)
                    distances.append(distance_row)
                return distances
    except Exception as e:
        print(f"Error getting distance matrix from Valhalla: {e}")
    
    # Fallback: Euclidean distance
    print("Warning: Using Euclidean distance fallback (less accurate)")
    distances = []
    for i, loc1 in enumerate(coords):
        row = []
        for j, loc2 in enumerate(coords):
            if i == j:
                row.append(0)
            else:
                # Approximate distance in meters
                lat_diff = (loc1[0] - loc2[0]) * 111000  # meters per degree latitude
                lon_diff = (loc1[1] - loc2[1]) * 111000 * 0.7  # adjusted for latitude
                dist = int((lat_diff**2 + lon_diff**2)**0.5)
                row.append(dist)
        distances.append(row)
    return distances


def solve_vrp(
    distance_matrix: List[List[int]],
    num_vehicles: int = 1,
    depot_index: int = 0,
    time_limit_seconds: int = 30
) -> Optional[Tuple[Dict, List[List[int]]]]:
    """
    Solve Vehicle Routing Problem using OR-Tools.
    
    Args:
        distance_matrix: Square matrix of distances between locations (in meters)
        num_vehicles: Number of vehicles in the fleet
        depot_index: Index of the depot (starting/ending location)
        time_limit_seconds: Maximum time to spend solving
    
    Returns:
        Tuple of (solution_data dict, routes list) or None if no solution found
    """
    num_locations = len(distance_matrix)
    
    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)
    
    # Define distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit_seconds
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        routes = extract_routes(manager, routing, solution)
        solution_data = {
            "status": "success",
            "total_distance_m": solution.ObjectiveValue(),
            "num_vehicles_used": len([r for r in routes if len(r) > 1])
        }
        return solution_data, routes
    
    return None


def extract_routes(manager, routing, solution) -> List[List[int]]:
    """
    Extract routes from OR-Tools solution.
    
    Args:
        manager: RoutingIndexManager instance
        routing: RoutingModel instance
        solution: Solution object from OR-Tools
    
    Returns:
        List of routes, where each route is a list of node indices
    """
    routes = []
    for vehicle_id in range(routing.vehicles()):
        route = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        # Add the end node (depot)
        end_node = manager.IndexToNode(index)
        if route:  # Only add end node if route has stops
            route.append(end_node)
        routes.append(route)
    
    # Filter out empty routes (vehicles not used)
    return [r for r in routes if len(r) > 1]


def wait_for_valhalla(valhalla_url: str = "http://valhalla:8002", max_retries: int = 30, retry_interval: int = 5):
    """
    Wait for Valhalla service to be ready.
    
    Args:
        valhalla_url: Base URL for Valhalla API
        max_retries: Maximum number of retry attempts
        retry_interval: Seconds to wait between retries
    """
    for i in range(max_retries):
        try:
            response = requests.get(f'{valhalla_url}/status', timeout=5)
            if response.status_code == 200:
                print("✓ Valhalla is ready")
                return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"Waiting for Valhalla... ({i+1}/{max_retries})")
                time.sleep(retry_interval)
            else:
                print(f"Warning: Valhalla not ready after {max_retries} attempts: {e}")
                return False
    return False
