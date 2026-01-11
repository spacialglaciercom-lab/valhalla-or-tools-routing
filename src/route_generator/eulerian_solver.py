"""Eulerian circuit solver for route generation"""

import networkx as nx
import logging
from typing import List, Tuple, Dict, Optional, Callable

logger = logging.getLogger(__name__)


class EulerianSolver:
    """Solve Eulerian circuit on road network"""
    
    def __init__(self, graph: nx.MultiDiGraph, 
                 node_coords: Optional[Dict[int, Tuple[float, float]]] = None,
                 prefer_right_turns: bool = True):
        """
        Initialize solver with a graph.
        Optimized: avoid unnecessary copies.
        
        Args:
            graph: The road network MultiDiGraph
            node_coords: Dict of {node_id: (lat, lon)} for turn cost calculation
            prefer_right_turns: If True, use turn-cost-aware algorithm (default: True)
        """
        # Store reference without copying (copy only if needed)
        self.working_graph = graph
        self.node_coords = node_coords or {}
        self.prefer_right_turns = prefer_right_turns
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
        if self.prefer_right_turns and self.node_coords:
            circuit = self._solve_with_turn_costs(start_node)
        else:
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
        This solves the Chinese Postman Problem using optimized matching.
        """
        # Find nodes with imbalanced degrees
        imbalanced = []
        
        for node in self.working_graph.nodes():
            in_degree = self.working_graph.in_degree(node)
            out_degree = self.working_graph.out_degree(node)
            diff = in_degree - out_degree
            
            if diff != 0:
                imbalanced.append((node, diff))
        
        # Separate deficit and surplus nodes with their counts
        deficit_list = [(n, diff) for n, diff in imbalanced if diff > 0]
        surplus_list = [(n, abs(diff)) for n, diff in imbalanced if diff < 0]
        
        if not deficit_list or not surplus_list:
            logger.warning("Graph has imbalanced nodes but no matching pairs")
            return
        
        # Create undirected graph for shortest path calculations (more efficient)
        undirected_graph = self.working_graph.to_undirected()
        
        # Optimized greedy matching: pair deficit to surplus nodes
        # Process largest imbalances first for better results
        deficit_list.sort(key=lambda x: x[1], reverse=True)
        surplus_list.sort(key=lambda x: x[1], reverse=True)
        
        deficit_idx = 0
        surplus_idx = 0
        
        while deficit_idx < len(deficit_list) and surplus_idx < len(surplus_list):
            deficit_node, deficit_count = deficit_list[deficit_idx]
            surplus_node, surplus_count = surplus_list[surplus_idx]
            
            # Calculate how many paths needed
            paths_needed = min(deficit_count, surplus_count)
            
            # Try to find shortest path (compute once per pair)
            try:
                path = nx.shortest_path(
                    undirected_graph,
                    source=deficit_node,
                    target=surplus_node
                )
                
                # Add edges along the path (repeat for multiple needed)
                for _ in range(paths_needed):
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        # Prefer existing edge direction
                        if self.working_graph.has_edge(u, v):
                            edge_data = self._get_edge_data(u, v)
                            self.working_graph.add_edge(u, v, **edge_data)
                            self.edges_added.append((u, v))
                        elif self.working_graph.has_edge(v, u):
                            edge_data = self._get_edge_data(v, u)
                            self.working_graph.add_edge(v, u, **edge_data)
                            self.edges_added.append((v, u))
                        else:
                            # Add undirected edge as bidirectional
                            edge_data = {'distance': 0.1}
                            self.working_graph.add_edge(u, v, **edge_data)
                            self.working_graph.add_edge(v, u, **edge_data)
                            self.edges_added.append((u, v))
                            
            except nx.NetworkXNoPath:
                logger.warning(f"No path between {deficit_node} and {surplus_node}")
                # Try next surplus node
                surplus_idx += 1
                continue
            
            # Update counts
            deficit_count -= paths_needed
            surplus_count -= paths_needed
            
            if deficit_count <= 0:
                deficit_idx += 1
            else:
                deficit_list[deficit_idx] = (deficit_node, deficit_count)
            
            if surplus_count <= 0:
                surplus_idx += 1
            else:
                surplus_list[surplus_idx] = (surplus_node, surplus_count)
        
        logger.info(f"Added {len(self.edges_added)} edges to make graph Eulerian")
    
    def _get_edge_data(self, u: int, v: int) -> Dict:
        """
        Get edge data from an existing edge.
        
        Args:
            u: Source node ID
            v: Target node ID
            
        Returns:
            Dictionary with edge attributes (default: {'distance': 0.1})
        """
        if self.working_graph.has_edge(u, v):
            try:
                # Get first edge data
                edges = self.working_graph.get_edge_data(u, v)
                if isinstance(edges, dict):
                    # Single edge or MultiDiGraph with single key
                    if 'distance' in edges:
                        return edges
                    # MultiDiGraph - get first edge data
                    if edges:
                        for key, data in edges.items():
                            if isinstance(data, dict):
                                return data
                            return edges if isinstance(edges, dict) else {'distance': 0.1}
            except (KeyError, AttributeError, TypeError) as e:
                logger.warning(f"Error getting edge data for ({u}, {v}): {e}")
        return {'distance': 0.1}
    
    def _find_start_node(self) -> int:
        """
        Find a suitable start node.
        Prefer node with maximum degree for better routing.
        
        Returns:
            Node ID to start from
            
        Raises:
            ValueError: If graph has no nodes
        """
        if self.working_graph.number_of_nodes() == 0:
            raise ValueError("Graph has no nodes - cannot find start node")
        
        try:
            # Start from node with highest total degree
            start_node = max(
                self.working_graph.nodes(),
                key=lambda n: self.working_graph.in_degree(n) + self.working_graph.out_degree(n)
            )
            return start_node
        except (ValueError, TypeError) as e:
            logger.error(f"Error finding start node: {e}")
            # Fallback: use first node
            return next(iter(self.working_graph.nodes()))
    
    def _solve_with_turn_costs(self, start_node: int) -> List[Tuple[int, int]]:
        """
        Custom Hierholzer's algorithm that selects next edges based on turn costs.
        Prefers right turns when multiple valid edges exist at a junction.
        
        Args:
            start_node: Starting node for the circuit
            
        Returns:
            List of (from_node, to_node) tuples representing the route
        """
        from .utils import bearing, turn_angle, turn_cost
        
        # Use NetworkX's eulerian_circuit but with turn-cost priority
        # Since NetworkX doesn't support custom edge selection, we'll use
        # a modified approach: build circuit while prioritizing low-cost edges
        graph = self.working_graph.copy()
        circuit = []
        current_node = start_node
        incoming_bearing = None
        
        # Helper to get all outgoing edges from a node
        def get_outgoing_edges(node):
            if node in graph:
                return list(graph.out_edges(node, keys=True))
            return []
        
        # Main loop: build circuit one edge at a time
        max_iterations = graph.number_of_edges() * 2  # Safety limit
        iteration = 0
        
        while graph.number_of_edges() > 0 and iteration < max_iterations:
            iteration += 1
            
            # Get available edges from current node
            available_edges = get_outgoing_edges(current_node)
            
            if not available_edges:
                # Dead end - find any node with remaining edges and continue
                for node in graph.nodes():
                    if graph.out_degree(node) > 0:
                        current_node = node
                        available_edges = get_outgoing_edges(node)
                        incoming_bearing = None  # Reset bearing at new start
                        break
                
                if not available_edges:
                    break  # No more edges
            
            # Select best edge based on turn cost
            best_edge = None
            best_cost = float('inf')
            
            for edge in available_edges:
                u, v, key = edge
                
                # Calculate turn cost
                cost = 1.0  # Default cost for first edge or missing coords
                if incoming_bearing is not None and u in self.node_coords and v in self.node_coords:
                    lat_u, lon_u = self.node_coords[u]
                    lat_v, lon_v = self.node_coords[v]
                    outgoing_bearing = bearing(lat_u, lon_u, lat_v, lon_v)
                    angle = turn_angle(incoming_bearing, outgoing_bearing)
                    cost = turn_cost(angle)
                
                # Prefer lower cost (right turns preferred)
                if cost < best_cost:
                    best_cost = cost
                    best_edge = edge
            
            if best_edge:
                u, v, key = best_edge
                
                # Add to circuit
                circuit.append((u, v))
                
                # Remove edge from graph
                graph.remove_edge(u, v, key)
                
                # Update incoming bearing for next iteration
                if u in self.node_coords and v in self.node_coords:
                    lat_u, lon_u = self.node_coords[u]
                    lat_v, lon_v = self.node_coords[v]
                    incoming_bearing = bearing(lat_u, lon_u, lat_v, lon_v)
                
                # Move to next node
                current_node = v
            else:
                break
        
        if iteration >= max_iterations:
            logger.warning(f"Turn-cost algorithm hit iteration limit. Using standard algorithm for remaining edges.")
            # Complete with standard algorithm if needed
            if graph.number_of_edges() > 0:
                remaining_circuit = list(nx.eulerian_circuit(graph))
                circuit.extend(remaining_circuit)
        
        return circuit
    
    def get_added_edges(self) -> List[Tuple[int, int]]:
        """
        Get list of edges added to make graph Eulerian.
        Returns a copy to prevent external modification.
        """
        return list(self.edges_added)  # More efficient than .copy() for lists
