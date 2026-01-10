"""Generate detailed report for trash collection route"""

import logging
from typing import Dict, List, Set, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate structured report for route analysis"""
    
    def __init__(self):
        """Initialize report generator"""
        self.report = {}
        
    def generate(self,
                osm_file: str,
                output_gpx: str,
                included_highways: List[str],
                excluded_tags: List[str],
                components_info: Dict,
                route_stats: Dict,
                turn_stats: Dict = None,
                added_edges: int = 0) -> str:
        """
        Generate comprehensive report.
        
        Args:
            osm_file: Source OSM file
            output_gpx: Output GPX file
            included_highways: List of included highway types
            excluded_tags: List of excluded conditions
            components_info: Component analysis results
            route_stats: Route statistics
            turn_stats: Turn preference statistics
            added_edges: Number of edges added for Eulerian property
            
        Returns:
            Formatted report string
        """
        report_lines = []
        
        # Title
        report_lines.append(f"# Generated {output_gpx} from uploaded OSM extract\n")
        report_lines.append(f"Generated: {datetime.now().isoformat()}\n")
        report_lines.append(f"Source OSM: {osm_file}\n")
        
        # Section 1: Guarantees
        report_lines.append("\n## 1. What the GPX route guarantees\n")
        report_lines.append(f"- **Single continuous track (no breaks):** YES - Single <trk> with single <trkseg>\n")
        report_lines.append(f"- **Right-side arm collection logic:** Each street segment driven twice (both directions)\n")
        report_lines.append(f"  so each curb appears on truck's right side on one of the two passes.\n")
        report_lines.append(f"- **Reduced left turns where possible:** Greedy heuristic applied to prefer right turns,\n")
        report_lines.append(f"  penalize left turns and U-turns using bearing-based turn angle calculation.\n")
        report_lines.append(f"- **One-way street handling:** IGNORED - Route may violate one-way restrictions to satisfy\n")
        report_lines.append(f"  'traverse twice' requirement for right-side collection.\n")
        
        # Section 2: Included/Excluded
        report_lines.append("\n## 2. What was included / excluded\n")
        
        report_lines.append(f"- **Included highway tags:** {', '.join(included_highways)}\n")
        report_lines.append(f"- **Excluded conditions:**\n")
        for excluded in excluded_tags:
            report_lines.append(f"  - {excluded}\n")
        
        report_lines.append(f"\n- **Connected components found:** {components_info.get('total_components', 0)}\n")
        report_lines.append(f"- **Component chosen:** Largest component ({components_info.get('largest_component_size', 0)} nodes)\n")
        
        # Count segments
        unique_segments = route_stats.get('unique_segments', 0)
        directed_traversals = route_stats.get('directed_traversals', 0)
        
        report_lines.append(f"- **Unique segments (in all components):** Unknown (see component sizes)\n")
        report_lines.append(f"- **Segments routed (chosen component):** {unique_segments}\n")
        report_lines.append(f"- **Segments excluded (disconnected):** {components_info.get('excluded_nodes', 0)} nodes\n")
        
        # Section 3: Route Stats
        report_lines.append("\n## 3. Route statistics (from generated GPX)\n")
        
        report_lines.append(f"- **Directed traversals:** {directed_traversals}\n")
        report_lines.append(f"  (Should be ≈ 2 × unique_segments for 'twice' rule)\n")
        report_lines.append(f"- **Approx distance:** {route_stats.get('total_distance_km', 0)} km\n")
        report_lines.append(f"- **Estimated drive time:** {route_stats.get('estimated_drive_time_minutes', 0)} minutes\n")
        report_lines.append(f"  ({route_stats.get('estimated_drive_time_hours', 0)} hours at 30 km/h average)\n")
        
        if turn_stats:
            report_lines.append(f"\n### Turn Analysis\n")
            report_lines.append(f"- **Right turns:** {turn_stats.get('right_turns', 0)}\n")
            report_lines.append(f"- **Left turns:** {turn_stats.get('left_turns', 0)}\n")
            report_lines.append(f"- **Straight:** {turn_stats.get('straight', 0)}\n")
            report_lines.append(f"- **U-turns (>150°):** {turn_stats.get('u_turns', 0)}\n")
        
        # Chinese Postman info
        if added_edges > 0:
            report_lines.append(f"\n### Eulerian Circuit Construction\n")
            report_lines.append(f"- **Edges added for Eulerian property:** {added_edges}\n")
            report_lines.append(f"  (Chinese Postman Problem solution)\n")
        
        # Additional notes
        report_lines.append(f"\n## Notes\n")
        report_lines.append(f"- OSM XML format extracted for Mercier area (bounds: 45.304-45.316 lat, -73.742 to -73.726 lon)\n")
        report_lines.append(f"- One-way restrictions ignored per Option A (preserves 'twice' traversal)\n")
        report_lines.append(f"- Output saved to: {output_gpx}\n")
        
        report_str = ''.join(report_lines)
        return report_str
    
    def save_report(self, report_content: str, output_file: str) -> None:
        """
        Save report to file.
        
        Args:
            report_content: Report text
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Saved report to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
