"""Utility functions for route generation"""

import math
from typing import Tuple
from functools import lru_cache


@lru_cache(maxsize=1024)
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    Optimized with LRU cache for repeated calculations.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    # Optimize: pre-compute radians
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dLat = lat2_r - lat1_r
    dLon = math.radians(lon2 - lon1)
    
    # Optimized Haversine with fewer trig calls
    sin_dLat_2 = math.sin(dLat / 2)
    sin_dLon_2 = math.sin(dLon / 2)
    
    a = sin_dLat_2 * sin_dLat_2 + \
        math.cos(lat1_r) * math.cos(lat2_r) * sin_dLon_2 * sin_dLon_2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


@lru_cache(maxsize=1024)
def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate bearing from point 1 to point 2 in degrees (0-360).
    North = 0, East = 90, South = 180, West = 270.
    Optimized with LRU cache.
    
    Args:
        lat1, lon1: Starting coordinate
        lat2, lon2: Ending coordinate
        
    Returns:
        Bearing in degrees
    """
    dLon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    
    # Cache trig values
    sin_lat1 = math.sin(lat1_rad)
    cos_lat1 = math.cos(lat1_rad)
    sin_lat2 = math.sin(lat2_rad)
    cos_lat2 = math.cos(lat2_rad)
    
    y = math.sin(dLon) * cos_lat2
    x = cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * math.cos(dLon)
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360) % 360
    
    return bearing_deg


@lru_cache(maxsize=2048)
def turn_angle(incoming_bearing: float, outgoing_bearing: float) -> float:
    """
    Calculate turn angle in degrees.
    Positive = right turn, Negative = left turn.
    Range: -180 to +180
    Optimized with cached lookups.
    
    Args:
        incoming_bearing: Bearing of incoming edge
        outgoing_bearing: Bearing of outgoing edge
        
    Returns:
        Turn angle in degrees
    """
    angle = outgoing_bearing - incoming_bearing
    
    # Optimize: use modulo instead of while loops (faster)
    angle = ((angle + 180) % 360) - 180
    
    return angle


def turn_cost(angle: float) -> float:
    """
    Calculate cost for a turn based on preference for right turns.
    Right turns = low cost
    Straight = medium cost
    Left turns/U-turns = high cost
    
    Args:
        angle: Turn angle in degrees
        
    Returns:
        Cost value (higher = less preferred)
    """
    abs_angle = abs(angle)
    
    # Right turn (0 to 90 degrees)
    if 0 <= angle <= 90:
        return 0.5 + (angle / 180)  # Prefer smaller right turns
    
    # Left turn (-90 to 0 degrees)
    elif -90 <= angle < 0:
        return 2.0 + (abs_angle / 90)  # Penalize left turns
    
    # Straight ahead (within tolerance)
    elif -10 <= angle <= 10:
        return 1.0  # Prefer straight
    
    # U-turn or wide angle (> 90)
    else:
        return 3.0 + (abs_angle / 180)  # Heavily penalize U-turns
