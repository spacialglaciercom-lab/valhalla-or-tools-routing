"""GPX file writer for routes"""

import logging
import gpxpy
import gpxpy.gpx
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class GPXWriter:
    """Write route to GPX file format"""
    
    def __init__(self, node_coords: Dict[int, Tuple[float, float]]):
        """
        Initialize writer.
        
        Args:
            node_coords: Dict of {node_id: (lat, lon)}
        """
        self.node_coords = node_coords
        
    def write_circuit(self, 
                     circuit: List[Tuple[int, int]],
                     output_file: str,
                     route_name: str = "Trash Collection Route") -> None:
        """
        Write Eulerian circuit to GPX file.
        Creates a single continuous track.
        
        Args:
            circuit: List of (from_node, to_node) edges
            output_file: Output GPX file path
            route_name: Name for the GPX track
        """
        gpx = gpxpy.gpx.GPX()
        gpx.name = route_name
        gpx.description = "Optimal trash collection route with right-side arm preference"
        
        # Create single track
        track = gpxpy.gpx.GPXTrack()
        track.name = route_name
        gpx.tracks.append(track)
        
        # Create segment
        segment = gpxpy.gpx.GPXTrackSegment()
        track.segments.append(segment)
        
        # Add all nodes from the circuit
        visited_nodes = set()
        
        for from_node, to_node in circuit:
            # Add from_node if first occurrence
            if from_node not in visited_nodes:
                if from_node in self.node_coords:
                    lat, lon = self.node_coords[from_node]
                    point = gpxpy.gpx.GPXTrackPoint(lat, lon)
                    segment.points.append(point)
                    visited_nodes.add(from_node)
            
            # Add to_node
            if to_node in self.node_coords:
                lat, lon = self.node_coords[to_node]
                point = gpxpy.gpx.GPXTrackPoint(lat, lon)
                segment.points.append(point)
                visited_nodes.add(to_node)
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                f.write(gpx.to_xml())
            logger.info(f"Wrote GPX file: {output_file}")
            logger.info(f"Track contains {len(segment.points)} waypoints")
        except Exception as e:
            logger.error(f"Failed to write GPX file: {e}")
            raise
    
    def get_track_stats(self, 
                       circuit: List[Tuple[int, int]]) -> Dict:
        """
        Calculate statistics for the circuit.
        
        Args:
            circuit: List of (from_node, to_node) edges
            
        Returns:
            Dictionary with statistics
        """
        total_distance = 0.0
        
        for from_node, to_node in circuit:
            if from_node in self.node_coords and to_node in self.node_coords:
                lat1, lon1 = self.node_coords[from_node]
                lat2, lon2 = self.node_coords[to_node]
                
                # Haversine distance
                from .utils import haversine_distance
                dist = haversine_distance(lat1, lon1, lat2, lon2)
                total_distance += dist
        
        # Estimate drive time (assume 30 km/h average)
        drive_time_hours = total_distance / 30.0
        drive_time_minutes = drive_time_hours * 60
        
        return {
            'directed_traversals': len(circuit),
            'unique_segments': len(circuit) // 2,  # Each segment traversed twice
            'total_distance_km': round(total_distance, 2),
            'estimated_drive_time_minutes': round(drive_time_minutes, 1),
            'estimated_drive_time_hours': round(drive_time_hours, 2)
        }
