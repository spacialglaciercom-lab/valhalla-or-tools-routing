"""Service wrapper for TrashRouteGenerator"""

import sys
import os
from pathlib import Path
from typing import Optional, Callable, Tuple
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.route_generator.trash_route_generator import TrashRouteGenerator
from ..models import Step, ProgressEvent
from ..services.progress_tracker import progress_tracker

logger = logging.getLogger(__name__)


class RouteGeneratorService:
    """Service wrapper for TrashRouteGenerator with progress tracking"""
    
    def __init__(self, job_id: str, osm_file: str, output_dir: str, config: dict):
        """
        Initialize route generator service
        
        Args:
            job_id: Job ID for progress tracking
            osm_file: Path to OSM file
            output_dir: Output directory for generated files
            config: Route generation configuration
        """
        self.job_id = job_id
        self.osm_file = osm_file
        self.output_dir = output_dir
        self.config = config
        
        # Create progress callback
        self.progress_callback = self._create_progress_callback()
        
        # Create generator
        self.generator = TrashRouteGenerator(
            osm_file=osm_file,
            output_dir=output_dir,
            ignore_oneway=config.get('ignore_oneway', True),
            prefer_right_turns=config.get('prefer_right_turns', True),
            progress_callback=self.progress_callback
        )
    
    def _create_progress_callback(self) -> Callable:
        """Create progress callback function"""
        def callback(step: str, progress: int, message: str, stats: Optional[dict] = None):
            try:
                # Map step string to Step enum
                step_enum = Step.PARSING
                if step == 'parsing':
                    step_enum = Step.PARSING
                elif step == 'building':
                    step_enum = Step.BUILDING
                elif step == 'analyzing':
                    step_enum = Step.ANALYZING
                elif step == 'solving':
                    step_enum = Step.SOLVING
                elif step == 'optimizing':
                    step_enum = Step.OPTIMIZING
                elif step == 'writing':
                    step_enum = Step.WRITING
                elif step == 'complete':
                    step_enum = Step.COMPLETE
                elif step == 'error':
                    step_enum = Step.ERROR
                
                # Update progress tracker
                progress_tracker.update_progress(self.job_id, step_enum, progress, message, stats)
                
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
        
        return callback
    
    def generate(self, output_gpx: str = "route.gpx", 
                 output_report: str = "report.md",
                 start_node: Optional[int] = None) -> Tuple[str, str]:
        """
        Generate route
        
        Args:
            output_gpx: Output GPX filename
            output_report: Output report filename
            start_node: Optional starting node ID
            
        Returns:
            Tuple of (gpx_path, report_path)
        """
        try:
            # Use start_node from config if not provided
            if start_node is None:
                start_node = self.config.get('start_node')
            
            # Generate route
            gpx_path, report_path = self.generator.generate(
                output_gpx=output_gpx,
                output_report=output_report,
                start_node=start_node
            )
            
            return gpx_path, report_path
            
        except Exception as e:
            logger.error(f"Route generation failed: {e}")
            progress_tracker.set_error(self.job_id, str(e))
            raise
    
    def get_summary(self) -> dict:
        """Get generation summary"""
        return self.generator.get_summary()
