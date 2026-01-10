"""OSM data parser for road network extraction"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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
        """Initialize parser with OSM file path"""
        self.osm_file = osm_file
        self.nodes: Dict[int, Node] = {}
        self.ways: Dict[int, Way] = {}
        self.driveable_ways: Dict[int, Way] = {}
        
    def parse(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """
        Parse OSM file and return nodes and driveable ways.
        
        Returns:
            Tuple of (nodes dict, driveable_ways dict)
        """
        try:
            tree = ET.parse(self.osm_file)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Failed to parse OSM file: {e}")
            raise
        
        # Parse nodes
        for node_elem in root.findall('node'):
            try:
                node_id = int(node_elem.get('id'))
                lat = float(node_elem.get('lat'))
                lon = float(node_elem.get('lon'))
                self.nodes[node_id] = Node(node_id, lat, lon)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid node: {e}")
                continue
        
        logger.info(f"Parsed {len(self.nodes)} nodes")
        
        # Parse ways
        for way_elem in root.findall('way'):
            try:
                way_id = int(way_elem.get('id'))
                
                # Extract node references
                node_refs = []
                for nd in way_elem.findall('nd'):
                    try:
                        node_refs.append(int(nd.get('ref')))
                    except (ValueError, TypeError):
                        continue
                
                # Extract tags
                tags = {}
                for tag in way_elem.findall('tag'):
                    key = tag.get('k')
                    value = tag.get('v')
                    if key and value:
                        tags[key] = value
                
                way = Way(way_id, node_refs, tags)
                self.ways[way_id] = way
                
                # Check if driveable
                if self._is_driveable(way):
                    self.driveable_ways[way_id] = way
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid way: {e}")
                continue
        
        logger.info(f"Parsed {len(self.ways)} ways total")
        logger.info(f"Found {len(self.driveable_ways)} driveable ways")
        
        return self.nodes, self.driveable_ways
    
    def _is_driveable(self, way: Way) -> bool:
        """
        Check if a way is driveable based on tags.
        
        Args:
            way: Way object to check
            
        Returns:
            True if driveable, False otherwise
        """
        tags = way.tags
        
        # Check if it's explicitly non-driveable
        highway = tags.get('highway', '')
        if highway in self.NON_DRIVEABLE:
            return False
        
        # Must have highway tag and be in include list
        if highway not in self.HIGHWAY_INCLUDE:
            return False
        
        # Check service tag exclusions
        service = tags.get('service', '')
        if service in self.SERVICE_EXCLUDE:
            return False
        
        # Check for access restrictions
        access = tags.get('access', '')
        if access in {'private', 'no', 'restricted'}:
            return False
        
        # Must have at least 2 nodes
        if len(way.nodes) < 2:
            return False
        
        return True
    
    def get_way_oneway(self, way_id: int) -> str:
        """
        Get oneway tag for a way.
        Returns: '', 'yes', 'no', '-1', '1', etc.
        """
        if way_id not in self.ways:
            return ''
        return self.ways[way_id].tags.get('oneway', '')
    
    def get_road_segments(self) -> List[Tuple[int, int, float, float, float, float]]:
        """
        Extract road segments from driveable ways.
        
        Returns:
            List of (node_id_1, node_id_2, lat1, lon1, lat2, lon2) tuples
        """
        segments = []
        
        for way_id, way in self.driveable_ways.items():
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
                    node_2.lat, node_2.lon
                ))
        
        logger.info(f"Extracted {len(segments)} road segments")
        return segments
