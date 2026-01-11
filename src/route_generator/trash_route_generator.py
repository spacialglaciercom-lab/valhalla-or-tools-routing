"""Main trash collection route generator"""

import logging
import os
from pathlib import Path
from typing import Tuple, Optional, Callable, Dict, List

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
    
    def __init__(self, osm_file: str, output_dir: str = None,
                 ignore_oneway: bool = True,
                 prefer_right_turns: bool = True,
                 progress_callback: Optional[Callable[[str, int, str, Optional[Dict]], None]] = None):
        """
        Initialize route generator.
        
        Args:
            osm_file: Path to OSM file
            output_dir: Directory for output files (default: current directory)
            ignore_oneway: If True, ignore oneway restrictions (Option A). If False, respect them (Option B).
            prefer_right_turns: If True, use turn-cost-aware algorithm (default: True)
            progress_callback: Optional callback function(step, progress, message, stats) for progress updates
        """
        self.osm_file = osm_file
        self.output_dir = output_dir or os.getcwd()
        self.ignore_oneway = ignore_oneway
        self.prefer_right_turns = prefer_right_turns
        self.progress_callback = progress_callback
        
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
        logger.info(f"  Ignore oneway: {ignore_oneway} (Option {'A' if ignore_oneway else 'B'})")
        logger.info(f"  Prefer right turns: {prefer_right_turns}")
    
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
            self._progress("complete", 99, "Generating report...")
            report_path = self._generate_report(output_report, gpx_path)
            
            logger.info(f"\nRoute generation complete!")
            logger.info(f"  GPX file: {gpx_path}")
            logger.info(f"  Report: {report_path}")
            self._progress("complete", 100, "Route generation complete!", self.stats)
            
            return gpx_path, report_path
            
        except Exception as e:
            logger.error(f"Route generation failed: {e}")
            raise
    
    def _parse_osm(self) -> None:
        """Parse OSM file and extract road data"""
        self._progress("parsing", 10, "Parsing OSM file...")
        self.parser = OSMParser(self.osm_file)
        self.nodes, self.driveable_ways = self.parser.parse()
        self.segments = self.parser.get_road_segments()
        
        logger.info(f"Parsed OSM: {len(self.nodes)} nodes, {len(self.driveable_ways)} driveable ways")
        logger.info(f"Extracted {len(self.segments)} road segments")
        self._progress("parsing", 20, f"Parsed {len(self.nodes)} nodes, {len(self.driveable_ways)} ways",
                      {"nodes": len(self.nodes), "edges": len(self.segments)})
    
    def _build_graph(self) -> None:
        """Build road network graph from segments"""
        self._progress("building", 30, "Building road network graph...")
        self.graph_builder = GraphBuilder()
        
        # Process segments - handle both old format (6 elements) and new format (7 elements with oneway)
        oneway_count = 0
        for segment in self.segments:
            if len(segment) == 7:
                node_id_1, node_id_2, lat1, lon1, lat2, lon2, oneway_tag = segment
            else:
                # Backward compatibility with old format
                node_id_1, node_id_2, lat1, lon1, lat2, lon2 = segment[:6]
                oneway_tag = ''
            
            if oneway_tag and oneway_tag not in {'', 'no'}:
                oneway_count += 1
            
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            
            self.graph_builder.add_segment(
                node_id_1, node_id_2,
                lat1, lon1, lat2, lon2,
                distance,
                oneway=oneway_tag,
                ignore_oneway=self.ignore_oneway
            )
        
        stats = self.graph_builder.get_stats()
        logger.info(f"Built graph: {stats['nodes']} nodes, {stats['edges']} edges")
        if oneway_count > 0:
            logger.info(f"Processed {oneway_count} oneway segments (Option {'A' if self.ignore_oneway else 'B'})")
        self._progress("building", 40, f"Graph built: {stats['nodes']} nodes, {stats['edges']} edges",
                      {"nodes": stats['nodes'], "edges": stats['edges'], "oneway_count": oneway_count})
    
    def _analyze_components(self) -> None:
        """Analyze connected components and select largest"""
        self._progress("analyzing", 50, "Analyzing connected components...")
        graph = self.graph_builder.get_graph()
        self.component_analyzer = ComponentAnalyzer(graph)
        components_info = self.component_analyzer.analyze()
        
        # Count unique segments in all components
        segment_counts = self.component_analyzer.count_unique_segments_all_components()
        components_info['total_unique_segments'] = segment_counts['total_unique_segments']
        
        self.stats['components'] = components_info
        
        logger.info(f"Found {components_info['total_components']} components")
        logger.info(f"Largest: {components_info['largest_component_size']} nodes")
        logger.info(f"Excluded: {components_info['excluded_nodes']} nodes")
        logger.info(f"Total unique segments: {components_info['total_unique_segments']}")
        self._progress("analyzing", 60, f"Found {components_info['total_components']} components",
                      {"components": components_info['total_components']})
    
    def _solve_eulerian(self, start_node: int = None) -> None:
        """Solve Eulerian circuit on the largest component"""
        self._progress("solving", 65, "Solving Eulerian circuit...")
        # Get subgraph for largest component
        subgraph = self.component_analyzer.get_largest_component_subgraph()
        
        # Get node coordinates for turn-cost calculation
        node_coords = self.graph_builder.get_all_node_coords()
        
        # Solve circuit with turn-cost awareness if enabled
        self.eulerian_solver = EulerianSolver(
            subgraph,
            node_coords=node_coords if self.prefer_right_turns else None,
            prefer_right_turns=self.prefer_right_turns
        )
        self.circuit = self.eulerian_solver.solve(start_node)
        
        # Track start node and method
        if start_node is None:
            start_node = self.eulerian_solver._find_start_node()
            start_method = "auto"
        else:
            start_method = "user"
        
        self.stats['start_node'] = start_node
        self.stats['start_node_method'] = start_method
        
        added_edges = len(self.eulerian_solver.get_added_edges())
        self.stats['added_edges'] = added_edges
        
        logger.info(f"Solved Eulerian circuit: {len(self.circuit)} edge traversals")
        logger.info(f"Added {added_edges} edges for Eulerian property (Chinese Postman)")
        self._progress("solving", 80, f"Circuit solved: {len(self.circuit)} edges",
                      {"circuit_length": len(self.circuit)})
    
    def _optimize_turns(self) -> None:
        """Optimize route with turn preference heuristic"""
        self._progress("optimizing", 85, "Analyzing turn statistics...")
        node_coords = self.graph_builder.get_all_node_coords()
        self.turn_optimizer = TurnOptimizer(node_coords)
        
        # Optimize circuit (may be no-op if turn costs already applied during solving)
        self.circuit = self.turn_optimizer.optimize_circuit(self.circuit)
        
        # Compute statistics
        turn_stats = self.turn_optimizer.compute_turn_statistics(self.circuit)
        self.stats['turns'] = turn_stats
        
        logger.info(f"Turn analysis: {turn_stats['right_turns']} right, "
                   f"{turn_stats['left_turns']} left, "
                   f"{turn_stats['straight']} straight, "
                   f"{turn_stats['u_turns']} U-turns")
        self._progress("optimizing", 90, "Turn optimization complete")
    
    def _write_gpx(self, output_gpx: str) -> str:
        """Write circuit to GPX file"""
        self._progress("writing", 95, "Writing GPX file...")
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
        self._progress("writing", 98, f"GPX written: {route_stats['total_distance_km']} km")
        
        return output_path
    
    def _generate_report(self, output_report: str, gpx_file: str) -> str:
        """Generate detailed report"""
        if not output_report.endswith('.md'):
            output_report += '.md'
        
        output_path = os.path.join(self.output_dir, output_report)
        
        components_info = self.stats.get('components', {})
        report_content = self.report_generator.generate(
            osm_file=self.osm_file,
            output_gpx=os.path.basename(gpx_file),
            included_highways=list(self.HIGHWAY_INCLUDE),
            excluded_tags=self.EXCLUDED_CONDITIONS,
            components_info=components_info,
            route_stats=self.stats.get('route', {}),
            turn_stats=self.stats.get('turns', None),
            added_edges=self.stats.get('added_edges', 0),
            total_unique_segments=components_info.get('total_unique_segments', 0),
            start_node=self.stats.get('start_node'),
            start_node_method=self.stats.get('start_node_method', 'auto')
        )
        
        self.report_generator.save_report(report_content, output_path)
        
        logger.info(f"Report written: {output_path}")
        
        return output_path
    
    def _progress(self, step: str, progress: int, message: str, stats: Optional[Dict] = None) -> None:
        """Call progress callback if available"""
        if self.progress_callback:
            try:
                self.progress_callback(step, progress, message, stats)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def get_summary(self) -> dict:
        """Get summary of generation results"""
        return {
            'nodes_parsed': len(self.nodes),
            'driveable_ways': len(self.driveable_ways),
            'segments': len(self.segments),
            'circuit_edges': len(self.circuit),
            'stats': self.stats
        }
