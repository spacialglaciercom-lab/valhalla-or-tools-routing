#!/usr/bin/env python3
"""
FastAPI server for OR-Tools VRP solver with Valhalla integration
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

from vrp_solver import solve_vrp, get_distance_matrix, wait_for_valhalla

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
VALHALLA_URL = os.getenv('VALHALLA_API', 'http://valhalla:8002')
PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '0.0.0.0')

# Create FastAPI app
app = FastAPI(
    title="OR-Tools VRP Solver API",
    description="Vehicle Routing Problem solver using OR-Tools and Valhalla routing engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class Location(BaseModel):
    id: int
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    name: Optional[str] = None

class SolveRequest(BaseModel):
    locations: List[Location] = Field(..., min_length=1, description="List of locations to visit")
    num_vehicles: int = Field(1, ge=1, description="Number of vehicles in the fleet")
    depot_id: Optional[int] = Field(None, description="ID of the depot location (defaults to first location)")

class RouteStop(BaseModel):
    id: int
    latitude: float
    longitude: float
    name: Optional[str] = None

class Route(BaseModel):
    vehicle: int
    stops: List[RouteStop]
    distance_m: int

class SolveResponse(BaseModel):
    status: str
    total_distance_m: Optional[int] = None
    num_locations: int
    num_routes: int
    num_vehicles_used: Optional[int] = None
    routes: List[Route]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Wait for Valhalla to be ready on startup"""
    logger.info("Starting OR-Tools VRP Solver API")
    logger.info(f"Valhalla URL: {VALHALLA_URL}")
    wait_for_valhalla(VALHALLA_URL)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OR-Tools VRP Solver API",
        "version": "1.0.0",
        "status": "running",
        "valhalla_url": VALHALLA_URL
    }

@app.post("/api/v1/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    """
    Solve Vehicle Routing Problem.
    
    Accepts a list of locations and returns optimized routes for the specified number of vehicles.
    """
    try:
        locations = request.locations
        num_vehicles = request.num_vehicles
        depot_id = request.depot_id
        
        if len(locations) < 2:
            raise HTTPException(status_code=400, detail="At least 2 locations are required")
        
        # Convert locations to dict format for vrp_solver
        location_dicts = [
            {"latitude": loc.latitude, "longitude": loc.longitude}
            for loc in locations
        ]
        
        # Determine depot index
        if depot_id is not None:
            depot_index = next((i for i, loc in enumerate(locations) if loc.id == depot_id), None)
            if depot_index is None:
                raise HTTPException(status_code=400, detail=f"Depot ID {depot_id} not found in locations")
        else:
            depot_index = 0  # Default to first location
        
        # Get distance matrix from Valhalla
        logger.info(f"Fetching distance matrix for {len(locations)} locations from Valhalla")
        distance_matrix = get_distance_matrix(location_dicts, VALHALLA_URL)
        
        if distance_matrix is None:
            raise HTTPException(status_code=500, detail="Failed to get distance matrix from Valhalla")
        
        # Solve VRP
        logger.info(f"Solving VRP with {num_vehicles} vehicles, depot at index {depot_index}")
        result = solve_vrp(distance_matrix, num_vehicles, depot_index)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to solve VRP - no solution found")
        
        solution_data, routes = result
        
        # Build response
        response_routes = []
        for vehicle_id, route_indices in enumerate(routes):
            if len(route_indices) > 1:  # Only include routes with stops
                route_stops = [
                    RouteStop(
                        id=locations[idx].id,
                        latitude=locations[idx].latitude,
                        longitude=locations[idx].longitude,
                        name=locations[idx].name
                    )
                    for idx in route_indices
                ]
                
                # Calculate total distance for this route
                route_distance = 0
                for i in range(len(route_indices) - 1):
                    route_distance += distance_matrix[route_indices[i]][route_indices[i+1]]
                
                response_routes.append(
                    Route(
                        vehicle=vehicle_id + 1,
                        stops=route_stops,
                        distance_m=route_distance
                    )
                )
        
        return SolveResponse(
            status=solution_data["status"],
            total_distance_m=solution_data.get("total_distance_m"),
            num_locations=len(locations),
            num_routes=len(response_routes),
            num_vehicles_used=solution_data.get("num_vehicles_used"),
            routes=response_routes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solving VRP: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
