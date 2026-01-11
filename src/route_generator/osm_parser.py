"""OSM data parser for road network extraction"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

# Try to import pyrosm for PBF support
try:
    import pyrosm
    PYROSM_AVAILABLE = True
except ImportError:
    PYROSM_AVAILABLE = False
    logger.warning("pyrosm library not available. PBF files will not be supported. Install with: pip install pyrosm")


@dataclass
class Node:
    """OSM Node"""
    id: int
    lat: float
    lon: float


@dataclass
class Way:
    """OSM Way (street segment)"""
    id: int
    nodes: List[int]
    tags: Dict[str, str]


class OSMParser:
    """Parse OSM XML data"""
    
    # Highway types to include
    HIGHWAY_INCLUDE = {'residential', 'unclassified', 'service', 'tertiary', 'secondary'}
    
    # Service types to exclude
    SERVICE_EXCLUDE = {'parking_aisle', 'parking'}
    
    # Ways that are non-driveable
    NON_DRIVEABLE = {'footway', 'cycleway', 'steps', 'path', 'track', 'pedestrian'}
    
    def __init__(self, osm_file: str):
        """
        Initialize parser with OSM file path.
        Supports both OSM XML (.osm, .xml) and PBF (.pbf) formats.
        """
        self.osm_file = osm_file
        self.nodes: Dict[int, Node] = {}
        self.ways: Dict[int, Way] = {}
        self.driveable_ways: Dict[int, Way] = {}
        self.file_format = self._detect_format()
        
    def _detect_format(self) -> str:
        """Detect OSM file format from extension"""
        import os
        ext = os.path.splitext(self.osm_file)[1].lower()
        if ext == '.pbf':
            return 'pbf'
        return 'xml'
    
    def parse(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """
        Parse OSM file and return nodes and driveable ways.
        Supports both XML and PBF formats.
        Optimized with iterative parsing for memory efficiency.
        
        Returns:
            Tuple of (nodes dict, driveable_ways dict)
        """
        if self.file_format == 'pbf':
            return self._parse_pbf()
        
        try:
            tree = ET.parse(self.osm_file)
            root = tree.getroot()
            return self._parse_xml_root(root)
        except Exception as e:
            logger.error(f"Failed to parse OSM file: {e}")
            raise
    
    def _parse_pbf(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """
        Parse OSM PBF file format.
        Falls back to XML parsing if pyrosm not available.
        """
        try:
            import pyrosm
            logger.info("Using pyrosm for PBF parsing")
            return self._parse_pbf_with_pyrosm()
        except ImportError:
            logger.warning("pyrosm not available, attempting XML fallback")
            # Try as XML if PBF parsing fails
            try:
                tree = ET.parse(self.osm_file)
                root = tree.getroot()
                # Continue with XML parsing logic from parse()
                return self._parse_xml_root(root)
            except Exception as e:
                logger.error(f"Failed to parse PBF file: {e}")
                logger.error("Install pyrosm for PBF support: pip install pyrosm")
                raise
    
    def _parse_pbf_with_pyrosm(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """Parse PBF using pyrosm library"""
        import pyrosm
        
        # Initialize pyrosm OSM object
        osm = pyrosm.OSM(self.osm_file)
        
        try:
            # Get network with nodes (driving network)
            nodes_gdf, edges_gdf = osm.get_network(
                network_type="driving",
                nodes=True
            )
            
            # Extract nodes into our Node dict
            if nodes_gdf is not None and len(nodes_gdf) > 0:
                for idx, row in nodes_gdf.iterrows():
                    node_id = int(row.get('id', idx))
                    geometry = row.get('geometry')
                    if geometry is not None:
                        lat = float(geometry.y)
                        lon = float(geometry.x)
                        self.nodes[node_id] = Node(node_id, lat, lon)
            
            # Extract ways from edges
            # Edges have 'osmid' (way ID), 'u' and 'v' (node IDs), and tags
            if edges_gdf is not None and len(edges_gdf) > 0:
                # Group edges by way ID (osmid)
                way_groups = {}
                for idx, row in edges_gdf.iterrows():
                    way_id = int(row.get('osmid', idx))
                    
                    if way_id not in way_groups:
                        way_groups[way_id] = {
                            'node_ids': set(),  # Use set to collect unique node IDs
                            'edges': [],  # Store edges to reconstruct node sequence
                            'tags': {}
                        }
                    
                    # Get node IDs from u and v columns
                    u = row.get('u')
                    v = row.get('v')
                    if u is not None and pd.notna(u):
                        way_groups[way_id]['node_ids'].add(int(u))
                    if v is not None and pd.notna(v):
                        way_groups[way_id]['node_ids'].add(int(v))
                    
                    # Store edge for sequencing (u -> v)
                    if u is not None and v is not None and pd.notna(u) and pd.notna(v):
                        way_groups[way_id]['edges'].append((int(u), int(v)))
                    
                    # Extract tags (all columns except geometry and standard edge columns)
                    skip_cols = {'geometry', 'id', 'osmid', 'u', 'v', 'key', 'ref', 'length'}
                    for col in edges_gdf.columns:
                        if col not in skip_cols and pd.notna(row.get(col)):
                            value = row[col]
                            if value is not None:
                                way_groups[way_id]['tags'][col] = str(value)
                
                # Reconstruct ways from edge groups
                for way_id, data in way_groups.items():
                    node_ids = data['node_ids']
                    if len(node_ids) < 2:
                        continue
                    
                    # Try to reconstruct node sequence from edges
                    # Simple approach: just use sorted node IDs (not ideal but works)
                    # Better: use edges to build path, but simpler for now
                    node_refs = sorted(list(node_ids))  # Sort for consistency
                    
                    # If we have edge sequence, try to use it
                    if len(data['edges']) > 0:
                        # Build a simple path from edges
                        # Start with first edge, then follow chain
                        edge_list = data['edges']
                        if len(edge_list) > 0:
                            path = []
                            remaining_edges = edge_list.copy()
                            current_edge = remaining_edges.pop(0)
                            path = [current_edge[0], current_edge[1]]
                            
                            # Try to extend path
                            while remaining_edges:
                                found = False
                                for i, (u, v) in enumerate(remaining_edges):
                                    if u == path[-1]:
                                        path.append(v)
                                        remaining_edges.pop(i)
                                        found = True
                                        break
                                    elif v == path[0]:
                                        path.insert(0, u)
                                        remaining_edges.pop(i)
                                        found = True
                                        break
                                if not found:
                                    break
                            
                            if len(path) >= 2:
                                node_refs = path
                    
                    way = Way(way_id, node_refs, data['tags'])
                    self.ways[way_id] = way
                    
                    # Check if driveable
                    highway = data['tags'].get('highway', '')
                    if self._is_driveable_fast(way, highway, data['tags']):
                        self.driveable_ways[way_id] = way
            
        except Exception as e:
            logger.error(f"Error parsing PBF with pyrosm: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        logger.info(f"Parsed {len(self.nodes)} nodes")
        logger.info(f"Parsed {len(self.ways)} ways total")
        logger.info(f"Found {len(self.driveable_ways)} driveable ways")
        
        return self.nodes, self.driveable_ways
    
    def _parse_xml_root(self, root) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """Parse XML root element (extracted from parse() for reuse)"""
        # Use generator + dict comprehension for faster parsing
        # Parse nodes with minimal error handling overhead
        node_data = root.findall('node')
        for node_elem in node_data:
            try:
                node_id = int(node_elem.get('id'))
                lat = float(node_elem.get('lat'))
                lon = float(node_elem.get('lon'))
                self.nodes[node_id] = Node(node_id, lat, lon)
            except (ValueError, TypeError, AttributeError):
                continue  # Skip silently
        
        logger.info(f"Parsed {len(self.nodes)} nodes")
        
        # Cache filter checks for performance
        include = self.HIGHWAY_INCLUDE
        exclude_service = self.SERVICE_EXCLUDE
        non_driveable = self.NON_DRIVEABLE
        
        # Parse ways with optimized filtering
        way_data = root.findall('way')
        for way_elem in way_data:
            try:
                way_id = int(way_elem.get('id'))
                
                # Extract node references (optimized)
                node_refs = [int(nd.get('ref')) for nd in way_elem.findall('nd')
                            if nd.get('ref')]
                
                if not node_refs:
                    continue
                
                # Extract tags as dict comprehension (faster)
                tags = {tag.get('k'): tag.get('v') 
                       for tag in way_elem.findall('tag')
                       if tag.get('k') and tag.get('v')}
                
                way = Way(way_id, node_refs, tags)
                self.ways[way_id] = way
                
                # Quick pre-filter before full check (optimization)
                highway = tags.get('highway', '')
                if highway not in include and highway not in non_driveable:
                    continue
                
                # Check if driveable
                if self._is_driveable_fast(way, highway, tags):
                    self.driveable_ways[way_id] = way
                    
            except (ValueError, TypeError, AttributeError):
                continue  # Skip silently
        
        logger.info(f"Parsed {len(self.ways)} ways total")
        logger.info(f"Found {len(self.driveable_ways)} driveable ways")
        
        return self.nodes, self.driveable_ways
    
    def _is_driveable_fast(self, way: Way, highway: str, tags: Dict) -> bool:
        """Fast driveable check (optimized version of _is_driveable)"""
        # Check if it's explicitly non-driveable
        if highway in self.NON_DRIVEABLE:
            return False
        
        # Must have highway tag and be in include list
        if highway not in self.HIGHWAY_INCLUDE:
            return False
        
        # Quick service check
        if tags.get('service', '') in self.SERVICE_EXCLUDE:
            return False
        
        # Quick access check
        if tags.get('access', '') in {'private', 'no', 'restricted'}:
            return False
        
        # Must have at least 2 nodes
        return len(way.nodes) >= 2
    
    def get_way_oneway(self, way_id: int) -> str:
        """
        Get oneway tag for a way.
        Returns: '', 'yes', 'no', '-1', '1', etc.
        """
        if way_id not in self.ways:
            return ''
        return self.ways[way_id].tags.get('oneway', '')
    
    def get_road_segments(self) -> List[Tuple[int, int, float, float, float, float, str]]:
        """
        Extract road segments from driveable ways.
        
        Returns:
            List of (node_id_1, node_id_2, lat1, lon1, lat2, lon2, oneway_tag) tuples
        """
        segments = []
        
        for way_id, way in self.driveable_ways.items():
            oneway_tag = way.tags.get('oneway', '')
            for i in range(len(way.nodes) - 1):
                node_id_1 = way.nodes[i]
                node_id_2 = way.nodes[i + 1]
                
                # Check if nodes exist
                if node_id_1 not in self.nodes or node_id_2 not in self.nodes:
                    logger.warning(f"Way {way_id}: node reference not found")
                    continue
                
                node_1 = self.nodes[node_id_1]
                node_2 = self.nodes[node_id_2]
                
                segments.append((
                    node_id_1, node_id_2,
                    node_1.lat, node_1.lon,
                    node_2.lat, node_2.lon,
                    oneway_tag
                ))
        
        logger.info(f"Extracted {len(segments)} road segments")
        return segments
