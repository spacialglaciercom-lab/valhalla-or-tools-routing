@echo off
REM Quick launcher for Trash Collection Route Generator GUI
python gui\trash_route_gui.py
pause
"""OSM data parser for road network extraction - Optimized & Fixed"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

@dataclass
class Node:
    id: int
    lat: float
    lon: float

@dataclass
class Way:
    id: int
    nodes: List[int]
    tags: Dict[str, str]

class OSMParser:
    HIGHWAY_INCLUDE = {'residential', 'unclassified', 'service', 'tertiary', 'secondary'}
    SERVICE_EXCLUDE = {'parking_aisle', 'parking'}
    NON_DRIVEABLE = {'footway', 'cycleway', 'steps', 'path', 'track', 'pedestrian'}
    
    def __init__(self, osm_file: str):
        self.osm_file = osm_file
        self.nodes: Dict[int, Node] = {}
        self.ways: Dict[int, Way] = {}
        self.driveable_ways: Dict[int, Way] = {}
        self.file_format = 'pbf' if osm_file.lower().endswith('.pbf') else 'xml'
        
    def parse(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        if self.file_format == 'pbf':
            return self._parse_pbf()
        return self._parse_xml_iterative()
    
    def _parse_xml_iterative(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        """Parses XML using iterparse to save memory on large files."""
        context = ET.iterparse(self.osm_file, events=('end',))
        
        for event, elem in context:
            if elem.tag == 'node':
                try:
                    nid = int(elem.get('id'))
                    self.nodes[nid] = Node(nid, float(elem.get('lat')), float(elem.get('lon')))
                except: pass
                elem.clear()
                
            elif elem.tag == 'way':
                try:
                    wid = int(elem.get('id'))
                    tags = {t.get('k'): t.get('v') for t in elem.findall('tag')}
                    
                    # Filter early
                    hw = tags.get('highway', '')
                    if hw not in self.HIGHWAY_INCLUDE or hw in self.NON_DRIVEABLE:
                        elem.clear()
                        continue
                        
                    refs = [int(nd.get('ref')) for nd in elem.findall('nd')]
                    if len(refs) < 2: 
                        elem.clear()
                        continue
                        
                    way = Way(wid, refs, tags)
                    self.ways[wid] = way
                    
                    if self._is_driveable_fast(way, hw, tags):
                        self.driveable_ways[wid] = way
                except: pass
                elem.clear()
        
        return self.nodes, self.driveable_ways

    def _parse_pbf(self) -> Tuple[Dict[int, Node], Dict[int, Way]]:
        try:
            import pyrosm
        except ImportError:
            raise ImportError("Please install pyrosm: pip install pyrosm")

        osm = pyrosm.OSM(self.osm_file)
        
        # Get nodes
        nodes_gdf, edges_gdf = osm.get_network(network_type="driving", nodes=True)
        
        # 1. Store Nodes
        if nodes_gdf is not None:
            for _, row in nodes_gdf.iterrows():
                if row.geometry:
                    nid = int(row['id'])
                    self.nodes[nid] = Node(nid, row.geometry.y, row.geometry.x)
                    
        # 2. Reconstruct Ways correctly (Fixing previous bug)
        if edges_gdf is not None:
            # Group edges by OSM Way ID
            for osmid, group in edges_gdf.groupby('osmid'):
                # Handle single or multiple Way IDs (pyrosm can return list)
                way_id_list = [osmid] if isinstance(osmid, (int, str)) else osmid
                
                # Tags - take from first row
                first_row = group.iloc[0]
                tags = {c: str(first_row[c]) for c in group.columns 
                       if c not in ['geometry', 'u', 'v', 'osmid', 'length'] and pd.notna(first_row[c])}

                # Reconstruct path from edge segments (u -> v)
                edges = [(int(r.u), int(r.v)) for _, r in group.iterrows()]
                
                if not edges: continue
                
                # Build adjacency to find path
                adj = {}
                degrees = {}
                all_nodes = set()
                
                for u, v in edges:
                    adj[u] = v # Assuming simple linear ways for now
                    degrees[v] = degrees.get(v, 0) + 1
                    degrees[u] = degrees.get(u, 0)
                    all_nodes.add(u)
                    all_nodes.add(v)

                # Find start node (degree in 0 for u)
                start_node = next((n for n in all_nodes if degrees[n] == 0), edges[0][0])
                
                # Trace path
                ordered_nodes = [start_node]
                curr = start_node
                while curr in adj:
                    curr = adj[curr]
                    ordered_nodes.append(curr)
                    if curr == start_node: break # Cycle protection

                # Create Way
                # If osmid is a list, we might be creating multiple ways, but usually it's unique per row group
                wid = int(way_id_list) if isinstance(way_id_list, (int, str)) else int(way_id_list[0])
                
                way = Way(wid, ordered_nodes, tags)
                self.ways[wid] = way
                self.driveable_ways[wid] = way

        return self.nodes, self.driveable_ways

    def _is_driveable_fast(self, way: Way, highway: str, tags: Dict) -> bool:
        if tags.get('service') in self.SERVICE_EXCLUDE: return False
        if tags.get('access') in {'private', 'no'}: return False
        return True

    def get_road_segments(self) -> List[Tuple]:
        segments = []
        for way in self.driveable_ways.values():
            oneway = way.tags.get('oneway', '')
            for i in range(len(way.nodes) - 1):
                n1, n2 = way.nodes[i], way.nodes[i+1]
                if n1 in self.nodes and n2 in self.nodes:
                    node1, node2 = self.nodes[n1], self.nodes[n2]
                    segments.append((n1, n2, node1.lat, node1.lon, node2.lat, node2.lon, oneway))
        return segments
