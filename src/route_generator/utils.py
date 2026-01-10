"""Utility functions for route generation"""

import math
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate bearing from point 1 to point 2 in degrees (0-360).
    North = 0, East = 90, South = 180, West = 270.
    
    Args:
        lat1, lon1: Starting coordinate
        lat2, lon2: Ending coordinate
        
    Returns:
        Bearing in degrees
    """
    dLon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    
    y = math.sin(dLon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dLon)
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360) % 360
    
    return bearing_deg


def turn_angle(incoming_bearing: float, outgoing_bearing: float) -> float:
    """
    Calculate turn angle in degrees.
    Positive = right turn, Negative = left turn.
    Range: -180 to +180
    
    Args:
        incoming_bearing: Bearing of incoming edge
        outgoing_bearing: Bearing of outgoing edge
        
    Returns:
        Turn angle in degrees
    """
    angle = outgoing_bearing - incoming_bearing
    
    # Normalize to -180 to +180
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    
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
