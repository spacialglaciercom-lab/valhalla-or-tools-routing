"""Configuration for route generator"""

# Highway types to include in routing
HIGHWAY_INCLUDE = {
    'residential',
    'unclassified',
    'service',
    'tertiary',
    'secondary'
}

# Non-driveable highway types
NON_DRIVEABLE = {
    'footway',
    'cycleway',
    'steps',
    'path',
    'track',
    'pedestrian'
}

# Service tags to exclude
SERVICE_EXCLUDE = {
    'parking_aisle',
    'parking'
}

# Turn preference weights
# (used in turn cost calculation)
TURN_WEIGHTS = {
    'right_turn_multiplier': 0.5,      # Prefer right turns
    'left_turn_multiplier': 2.0,       # Penalize left turns
    'straight_multiplier': 1.0,        # Neutral for straight
    'u_turn_multiplier': 3.0           # Heavily penalize U-turns
}

# Routing parameters
AVERAGE_SPEED_KMH = 30  # Assumed average speed for time estimation
STRAIGHT_THRESHOLD = 10  # Degrees - angles below this considered straight

# Chinese Postman Problem solver parameters
CPP_SOLVER = 'greedy'  # 'greedy' or 'optimal' (greedy is faster)
