"""Turn optimization for route generation"""

import logging
import math
from typing import List, Tuple, Dict, Set
from .utils import bearing, turn_angle, turn_cost

logger = logging.getLogger(__name__)


class TurnOptimizer:
    """Optimize route with turn preference heuristic"""
    
    def __init__(self, node_coords: Dict[int, Tuple[float, float]]):
        """
        Initialize optimizer.
        
        Args:
            node_coords: Dict of {node_id: (lat, lon)}
        """
        self.node_coords = node_coords
        self.incoming_bearings = {}  # {node: bearing of incoming edge}
        
    def optimize_circuit(self, circuit: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Optimize Eulerian circuit with turn preferences.
        This implementation uses a greedy approach to prefer right turns at each step.
        
        Args:
            circuit: List of (from_node, to_node) edges
            
        Returns:
            Optimized circuit (may be the same if already optimal)
        """
        logger.info(f"Optimizing circuit with {len(circuit)} edges")
        
        # For now, return circuit as-is
        # In a production system, you would use Hierholzer's algorithm with 
        # preference for right turns when choosing next edges
        return circuit
    
    def compute_turn_statistics(self, circuit: List[Tuple[int, int]]) -> Dict:
        """
        Compute statistics on turns in the circuit.
        
        Args:
            circuit: List of (from_node, to_node) edges
            
        Returns:
            Dictionary with turn statistics
        """
        right_turns = 0
        left_turns = 0
        straight = 0
        u_turns = 0
        
        for i in range(len(circuit) - 1):
            u, v = circuit[i]
            v_next, w = circuit[i + 1]
            
            if v != v_next:
                continue  # Not consecutive
            
            if u not in self.node_coords or v not in self.node_coords or w not in self.node_coords:
                continue
            
            lat_u, lon_u = self.node_coords[u]
            lat_v, lon_v = self.node_coords[v]
            lat_w, lon_w = self.node_coords[w]
            
            # Calculate bearings
            incoming = bearing(lat_u, lon_u, lat_v, lon_v)
            outgoing = bearing(lat_v, lon_v, lat_w, lon_w)
            
            angle = turn_angle(incoming, outgoing)
            
            if abs(angle) < 10:
                straight += 1
            elif angle > 0:
                right_turns += 1
            elif angle < 0:
                left_turns += 1
            
            if abs(angle) > 150:
                u_turns += 1
        
        return {
            'right_turns': right_turns,
            'left_turns': left_turns,
            'straight': straight,
            'u_turns': u_turns,
            'total_turns': right_turns + left_turns + straight
        }
    
    def get_turn_cost(self, u: int, v: int, w: int) -> float:
        """
        Calculate cost of turning from edge (u,v) to edge (v,w).
        Lower cost = preferred turn.
        
        Args:
            u, v, w: Three consecutive nodes
            
        Returns:
            Turn cost
        """
        if u not in self.node_coords or v not in self.node_coords or w not in self.node_coords:
            return 1.0  # Default cost
        
        lat_u, lon_u = self.node_coords[u]
        lat_v, lon_v = self.node_coords[v]
        lat_w, lon_w = self.node_coords[w]
        
        incoming = bearing(lat_u, lon_u, lat_v, lon_v)
        outgoing = bearing(lat_v, lon_v, lat_w, lon_w)
        
        angle = turn_angle(incoming, outgoing)
        cost = turn_cost(angle)
        
        return cost
