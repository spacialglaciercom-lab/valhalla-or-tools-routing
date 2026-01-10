"""Eulerian circuit solver for route generation"""

import networkx as nx
import logging
from typing import List, Tuple, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class EulerianSolver:
    """Solve Eulerian circuit on road network"""
    
    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initialize solver with a graph.
        Optimized: avoid unnecessary copies.
        
        Args:
            graph: The road network MultiDiGraph
        """
        # Store reference without copying (copy only if needed)
        self.working_graph = graph
        self.edges_added = []
        self._graph_modified = False
        
    def solve(self, start_node: int = None) -> List[Tuple[int, int]]:
        """
        Find Eulerian circuit in the graph.
        If the graph is not Eulerian, add minimum edges to make it Eulerian (Chinese Postman).
        
        Args:
            start_node: Starting node for the circuit (if None, uses first node)
            
        Returns:
            List of (from_node, to_node) tuples representing the route
        """
        # Check if graph is Eulerian
        if self._is_eulerian():
            logger.info("Graph is already Eulerian")
        else:
            logger.info("Graph is not Eulerian, applying Chinese Postman solution")
            self._make_eulerian()
        
        # Find start node
        if start_node is None:
            start_node = self._find_start_node()
        
        logger.info(f"Starting Eulerian circuit from node {start_node}")
        
        # Find Eulerian circuit
        circuit = list(nx.eulerian_circuit(self.working_graph, source=start_node))
        
        logger.info(f"Generated Eulerian circuit with {len(circuit)} edge traversals")
        return circuit
    
    def _is_eulerian(self) -> bool:
        """
        Check if graph is Eulerian (all nodes have equal in-degree and out-degree).
        Optimized: use NetworkX built-in check.
        
        Returns:
            True if Eulerian, False otherwise
        """
        # Use NetworkX optimized Eulerian check
        try:
            return nx.is_eulerian(self.working_graph)
        except:
            # Fallback: manual check for compatibility
            for node in self.working_graph.nodes():
                if self.working_graph.in_degree(node) != self.working_graph.out_degree(node):
                    return False
            return True
    
    def _make_eulerian(self) -> None:
        """
        Make the graph Eulerian by adding duplicate edges.
        This solves the Chinese Postman Problem.
        """
        # Find nodes with imbalanced degrees
        imbalanced = []
        
        for node in self.working_graph.nodes():
            in_degree = self.working_graph.in_degree(node)
            out_degree = self.working_graph.out_degree(node)
            
            if in_degree != out_degree:
                imbalanced.append((node, in_degree - out_degree))
        
        # Pair up imbalanced nodes and find shortest paths between them
        deficit_nodes = [n for n, diff in imbalanced if diff > 0]
        surplus_nodes = [n for n, diff in imbalanced if diff < 0]
        
        # Simple greedy matching of deficit to surplus
        for surplus_node in surplus_nodes:
            for deficit_node in deficit_nodes:
                try:
                    # Try to find shortest path
                    path = nx.shortest_path(
                        self.working_graph.to_undirected(),
                        source=deficit_node,
                        target=surplus_node
                    )
                    
                    # Add edges along the path
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        # Find an edge from u to v
                        if self.working_graph.has_edge(u, v):
                            self.working_graph.add_edge(u, v, **self._get_edge_data(u, v))
                            self.edges_added.append((u, v))
                        elif self.working_graph.has_edge(v, u):
                            self.working_graph.add_edge(v, u, **self._get_edge_data(v, u))
                            self.edges_added.append((v, u))
                    
                except nx.NetworkXNoPath:
                    logger.warning(f"No path between {deficit_node} and {surplus_node}")
        
        logger.info(f"Added {len(self.edges_added)} edges to make graph Eulerian")
    
    def _get_edge_data(self, u: int, v: int) -> Dict:
        """Get edge data from an existing edge"""
        if self.working_graph.has_edge(u, v):
            # Get first edge data
            edges = self.working_graph.get_edge_data(u, v)
            if isinstance(edges, dict):
                # Single edge
                return edges
            else:
                # MultiDiGraph - get first edge
                for key, data in edges.items():
                    return data
        return {'distance': 0.1}
    
    def _find_start_node(self) -> int:
        """
        Find a suitable start node.
        Prefer node with maximum degree.
        
        Returns:
            Node ID to start from
        """
        if self.working_graph.number_of_nodes() == 0:
            raise ValueError("Graph has no nodes")
        
        # Start from node with highest total degree
        start_node = max(
            self.working_graph.nodes(),
            key=lambda n: self.working_graph.in_degree(n) + self.working_graph.out_degree(n)
        )
        
        return start_node
    
    def get_added_edges(self) -> List[Tuple[int, int]]:
        """Get list of edges added to make graph Eulerian"""
        return self.edges_added.copy()
