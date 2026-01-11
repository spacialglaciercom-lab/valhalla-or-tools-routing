"""Build graph from road segments for routing"""

import networkx as nx
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Build and manage road network graph"""
    
    def __init__(self):
        """Initialize graph builder"""
        self.graph = nx.MultiDiGraph()
        self.node_coords = {}  # {node_id: (lat, lon)}
        
    def add_segment(self, 
                   node_id_1: int, node_id_2: int,
                   lat1: float, lon1: float,
                   lat2: float, lon2: float,
                   distance: float = None,
                   oneway: str = '',
                   ignore_oneway: bool = True) -> None:
        """
        Add a segment to the graph.
        Per the "twice" requirement, each segment is traversed twice (both directions)
        unless oneway restrictions are respected.
        
        Args:
            node_id_1: First node ID
            node_id_2: Second node ID
            lat1, lon1: First node coordinates
            lat2, lon2: Second node coordinates
            distance: Optional distance value
            oneway: Oneway tag value ('yes', 'no', '-1', '1', etc.)
            ignore_oneway: If True, always add bidirectional edges (Option A). 
                          If False, respect oneway restrictions (Option B).
        """
        # Store coordinates
        if node_id_1 not in self.node_coords:
            self.node_coords[node_id_1] = (lat1, lon1)
        if node_id_2 not in self.node_coords:
            self.node_coords[node_id_2] = (lat2, lon2)
        
        # Determine if we should add reverse edge
        is_oneway = oneway in {'yes', '1', 'true', '1'}
        is_reverse_oneway = oneway in {'-1', '-true'}
        
        # Add forward edge
        forward_edge_data = {
            'lat1': lat1, 'lon1': lon1,
            'lat2': lat2, 'lon2': lon2,
            'distance': distance if distance else 0.1,
            'oneway': oneway
        }
        self.graph.add_edge(node_id_1, node_id_2, **forward_edge_data)
        
        # Add reverse edge if:
        # - ignore_oneway is True (Option A), OR
        # - ignore_oneway is False AND not oneway (Option B)
        if ignore_oneway or (not is_oneway and not is_reverse_oneway):
            reverse_edge_data = {
                'lat1': lat2, 'lon1': lon2,
                'lat2': lat1, 'lon2': lon1,
                'distance': distance if distance else 0.1,
                'oneway': oneway
            }
            self.graph.add_edge(node_id_2, node_id_1, **reverse_edge_data)
    
    def get_graph(self) -> nx.MultiDiGraph:
        """Get the constructed graph"""
        return self.graph
    
    def get_node_coords(self, node_id: int) -> Tuple[float, float]:
        """Get (lat, lon) for a node"""
        return self.node_coords.get(node_id, (0.0, 0.0))
    
    def get_all_node_coords(self) -> Dict[int, Tuple[float, float]]:
        """
        Get all node coordinates.
        Returns reference to avoid unnecessary copy when caller won't modify.
        """
        return self.node_coords
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'node_count': len(self.node_coords)
        }
