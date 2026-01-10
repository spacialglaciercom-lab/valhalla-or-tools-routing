"""Main trash collection route generator"""

import logging
import os
from pathlib import Path
from typing import Tuple, Optional

from .osm_parser import OSMParser
from .graph_builder import GraphBuilder
from .component_analyzer import ComponentAnalyzer
from .eulerian_solver import EulerianSolver
from .turn_optimizer import TurnOptimizer
from .gpx_writer import GPXWriter
from .report_generator import ReportGenerator
from .utils import haversine_distance

logger = logging.getLogger(__name__)


class TrashRouteGenerator:
    """Main orchestrator for trash collection route generation"""
    
    # Configuration
    HIGHWAY_INCLUDE = {'residential', 'unclassified', 'service', 'tertiary', 'secondary'}
    EXCLUDED_CONDITIONS = [
        'service=parking_aisle',
        'service=parking',
        'highway=footway',
        'highway=cycleway',
        'highway=steps',
        'highway=path',
        'highway=track',
        'highway=pedestrian',
        'access=private'
    ]
    
    def __init__(self, osm_file: str, output_dir: str = None):
        """
        Initialize route generator.
        
        Args:
            osm_file: Path to OSM file
            output_dir: Directory for output files (default: current directory)
        """
        self.osm_file = osm_file
        self.output_dir = output_dir or os.getcwd()
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.parser = None
        self.graph_builder = None
        self.component_analyzer = None
        self.eulerian_solver = None
        self.turn_optimizer = None
        self.gpx_writer = None
        self.report_generator = ReportGenerator()
        
        # Results storage
        self.nodes = {}
        self.driveable_ways = {}
        self.segments = []
        self.circuit = []
        self.stats = {}
        
        logger.info(f"Initialized TrashRouteGenerator")
        logger.info(f"  OSM file: {osm_file}")
        logger.info(f"  Output dir: {self.output_dir}")
    
    def generate(self, 
                 output_gpx: str = "trash_collection_route.gpx",
                 output_report: str = "route_report.md",
                 start_node: int = None) -> Tuple[str, str]:
        """
        Generate the trash collection route.
        
        Args:
            output_gpx: Name of output GPX file
            output_report: Name of output report file
            start_node: Optional starting node ID
            
        Returns:
            Tuple of (gpx_file_path, report_file_path)
        """
        logger.info("Starting route generation pipeline...")
        
        try:
            # Step 1: Parse OSM data
            logger.info("\n[Step 1] Parsing OSM data...")
            self._parse_osm()
            
            # Step 2: Build graph
            logger.info("\n[Step 2] Building road network graph...")
            self._build_graph()
            
            # Step 3: Analyze components
            logger.info("\n[Step 3] Analyzing connected components...")
            self._analyze_components()
            
            # Step 4: Solve Eulerian circuit
            logger.info("\n[Step 4] Solving Eulerian circuit...")
            self._solve_eulerian(start_node)
            
            # Step 5: Optimize with turn preferences
            logger.info("\n[Step 5] Optimizing with turn preferences...")
            self._optimize_turns()
            
            # Step 6: Write GPX
            logger.info("\n[Step 6] Writing GPX file...")
            gpx_path = self._write_gpx(output_gpx)
            
            # Step 7: Generate report
            logger.info("\n[Step 7] Generating report...")
            report_path = self._generate_report(output_report, gpx_path)
            
            logger.info(f"\nRoute generation complete!")
            logger.info(f"  GPX file: {gpx_path}")
            logger.info(f"  Report: {report_path}")
            
            return gpx_path, report_path
            
        except Exception as e:
            logger.error(f"Route generation failed: {e}")
            raise
    
    def _parse_osm(self) -> None:
        """Parse OSM file and extract road data"""
        self.parser = OSMParser(self.osm_file)
        self.nodes, self.driveable_ways = self.parser.parse()
        self.segments = self.parser.get_road_segments()
        
        logger.info(f"Parsed OSM: {len(self.nodes)} nodes, {len(self.driveable_ways)} driveable ways")
        logger.info(f"Extracted {len(self.segments)} road segments")
    
    def _build_graph(self) -> None:
        """Build road network graph from segments"""
        self.graph_builder = GraphBuilder()
        
        for node_id_1, node_id_2, lat1, lon1, lat2, lon2 in self.segments:
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            self.graph_builder.add_segment(
                node_id_1, node_id_2,
                lat1, lon1, lat2, lon2,
                distance
            )
        
        stats = self.graph_builder.get_stats()
        logger.info(f"Built graph: {stats['nodes']} nodes, {stats['edges']} edges")
    
    def _analyze_components(self) -> None:
        """Analyze connected components and select largest"""
        graph = self.graph_builder.get_graph()
        self.component_analyzer = ComponentAnalyzer(graph)
        components_info = self.component_analyzer.analyze()
        
        self.stats['components'] = components_info
        
        logger.info(f"Found {components_info['total_components']} components")
        logger.info(f"Largest: {components_info['largest_component_size']} nodes")
        logger.info(f"Excluded: {components_info['excluded_nodes']} nodes")
    
    def _solve_eulerian(self, start_node: int = None) -> None:
        """Solve Eulerian circuit on the largest component"""
        # Get subgraph for largest component
        subgraph = self.component_analyzer.get_largest_component_subgraph()
        
        # Solve circuit
        self.eulerian_solver = EulerianSolver(subgraph)
        self.circuit = self.eulerian_solver.solve(start_node)
        
        added_edges = len(self.eulerian_solver.get_added_edges())
        self.stats['added_edges'] = added_edges
        
        logger.info(f"Solved Eulerian circuit: {len(self.circuit)} edge traversals")
        logger.info(f"Added {added_edges} edges for Eulerian property (Chinese Postman)")
    
    def _optimize_turns(self) -> None:
        """Optimize route with turn preference heuristic"""
        node_coords = self.graph_builder.get_all_node_coords()
        self.turn_optimizer = TurnOptimizer(node_coords)
        
        # Optimize circuit
        self.circuit = self.turn_optimizer.optimize_circuit(self.circuit)
        
        # Compute statistics
        turn_stats = self.turn_optimizer.compute_turn_statistics(self.circuit)
        self.stats['turns'] = turn_stats
        
        logger.info(f"Turn analysis: {turn_stats['right_turns']} right, "
                   f"{turn_stats['left_turns']} left, "
                   f"{turn_stats['straight']} straight, "
                   f"{turn_stats['u_turns']} U-turns")
    
    def _write_gpx(self, output_gpx: str) -> str:
        """Write circuit to GPX file"""
        if not output_gpx.endswith('.gpx'):
            output_gpx += '.gpx'
        
        output_path = os.path.join(self.output_dir, output_gpx)
        
        node_coords = self.graph_builder.get_all_node_coords()
        self.gpx_writer = GPXWriter(node_coords)
        
        self.gpx_writer.write_circuit(
            self.circuit,
            output_path,
            "Trash Collection Route - Right-Side Arm Optimized"
        )
        
        # Get track stats
        route_stats = self.gpx_writer.get_track_stats(self.circuit)
        self.stats['route'] = route_stats
        
        logger.info(f"GPX written: {output_path}")
        logger.info(f"  Distance: {route_stats['total_distance_km']} km")
        logger.info(f"  Est. time: {route_stats['estimated_drive_time_minutes']} min")
        
        return output_path
    
    def _generate_report(self, output_report: str, gpx_file: str) -> str:
        """Generate detailed report"""
        if not output_report.endswith('.md'):
            output_report += '.md'
        
        output_path = os.path.join(self.output_dir, output_report)
        
        report_content = self.report_generator.generate(
            osm_file=self.osm_file,
            output_gpx=os.path.basename(gpx_file),
            included_highways=list(self.HIGHWAY_INCLUDE),
            excluded_tags=self.EXCLUDED_CONDITIONS,
            components_info=self.stats.get('components', {}),
            route_stats=self.stats.get('route', {}),
            turn_stats=self.stats.get('turns', None),
            added_edges=self.stats.get('added_edges', 0)
        )
        
        self.report_generator.save_report(report_content, output_path)
        
        logger.info(f"Report written: {output_path}")
        
        return output_path
    
    def get_summary(self) -> dict:
        """Get summary of generation results"""
        return {
            'nodes_parsed': len(self.nodes),
            'driveable_ways': len(self.driveable_ways),
            'segments': len(self.segments),
            'circuit_edges': len(self.circuit),
            'stats': self.stats
        }
