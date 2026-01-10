"""Analyze connected components in the road network"""

import networkx as nx
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class ComponentAnalyzer:
    """Analyze and select connected components from the road graph"""
    
    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initialize analyzer with a graph.
        
        Args:
            graph: The road network MultiDiGraph
        """
        self.graph = graph
        self.weakly_connected_components = None
        self.largest_component_nodes = None
        
    def analyze(self) -> Dict[str, any]:
        """
        Analyze connected components.
        
        Returns:
            Dictionary with component information
        """
        # Get weakly connected components (ignoring direction)
        self.weakly_connected_components = list(
            nx.weakly_connected_components(self.graph)
        )
        
        components_info = {
            'total_components': len(self.weakly_connected_components),
            'component_sizes': []
        }
        
        for i, component in enumerate(self.weakly_connected_components):
            components_info['component_sizes'].append(len(component))
            logger.info(f"Component {i}: {len(component)} nodes")
        
        # Select largest component
        self.largest_component_nodes = max(
            self.weakly_connected_components,
            key=len
        )
        
        components_info['largest_component_size'] = len(self.largest_component_nodes)
        components_info['excluded_nodes'] = sum(
            len(c) for c in self.weakly_connected_components 
            if c != self.largest_component_nodes
        )
        
        logger.info(f"Largest component: {len(self.largest_component_nodes)} nodes")
        logger.info(f"Excluded nodes: {components_info['excluded_nodes']}")
        
        return components_info
    
    def get_largest_component_subgraph(self) -> nx.MultiDiGraph:
        """
        Get subgraph containing only the largest connected component.
        
        Returns:
            Subgraph as MultiDiGraph
        """
        if self.largest_component_nodes is None:
            self.analyze()
        
        subgraph = self.graph.subgraph(self.largest_component_nodes).copy()
        return subgraph
    
    def get_excluded_components(self) -> List[Set[int]]:
        """
        Get all components except the largest.
        
        Returns:
            List of node sets for excluded components
        """
        if self.largest_component_nodes is None:
            self.analyze()
        
        return [c for c in self.weakly_connected_components 
                if c != self.largest_component_nodes]
    
    def count_edges_in_component(self, component_nodes: Set[int]) -> int:
        """
        Count edges in a specific component.
        
        Args:
            component_nodes: Set of node IDs in component
            
        Returns:
            Number of edges
        """
        subgraph = self.graph.subgraph(component_nodes)
        return subgraph.number_of_edges()
    
    def count_unique_segments_all_components(self) -> Dict[str, int]:
        """
        Count unique road segments (undirected edges) in all components.
        Since graph has bidirectional edges, unique segments = total_edges / 2.
        
        Returns:
            Dictionary with total unique segments across all components
        """
        total_edges = self.graph.number_of_edges()
        # Each segment appears twice (bidirectional), so unique = edges / 2
        total_unique_segments = total_edges // 2
        
        # Count per component
        component_segments = {}
        for i, component in enumerate(self.weakly_connected_components):
            edges = self.count_edges_in_component(component)
            unique = edges // 2
            component_segments[f'component_{i}'] = unique
        
        return {
            'total_unique_segments': total_unique_segments,
            'component_segments': component_segments,
            'total_edges': total_edges
        }
