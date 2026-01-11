"""
Unit tests for TrashRouteGenerator
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.route_generator.trash_route_generator import TrashRouteGenerator


@pytest.fixture
def sample_osm_file():
    """Create a sample OSM XML file for testing"""
    osm_content = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="37.7749" lon="-122.4194"/>
  <node id="2" lat="37.7750" lon="-122.4195"/>
  <node id="3" lat="37.7751" lon="-122.4196"/>
  <node id="4" lat="37.7748" lon="-122.4193"/>
  <way id="1">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="residential"/>
  </way>
  <way id="2">
    <nd ref="2"/>
    <nd ref="3"/>
    <tag k="highway" v="residential"/>
  </way>
  <way id="3">
    <nd ref="3"/>
    <nd ref="4"/>
    <tag k="highway" v="residential"/>
  </way>
  <way id="4">
    <nd ref="4"/>
    <nd ref="1"/>
    <tag k="highway" v="residential"/>
  </way>
</osm>
"""
    temp_dir = tempfile.mkdtemp()
    osm_path = Path(temp_dir) / "test.osm"
    osm_path.write_text(osm_content)
    yield osm_path
    # Cleanup
    shutil.rmtree(temp_dir) if os.path.exists(temp_dir) else None


def test_generator_initialization(sample_osm_file, tmp_path):
    """Test TrashRouteGenerator initialization"""
    generator = TrashRouteGenerator(
        str(sample_osm_file),
        str(tmp_path),
        ignore_oneway=True,
        prefer_right_turns=True
    )
    
    assert generator.osm_file == str(sample_osm_file)
    assert generator.output_dir == str(tmp_path)
    assert generator.ignore_oneway is True
    assert generator.prefer_right_turns is True


def test_generator_with_progress_callback(sample_osm_file, tmp_path):
    """Test generator with progress callback"""
    progress_steps = []
    
    def progress_callback(step, progress, message, stats=None):
        progress_steps.append((step, progress, message))
    
    generator = TrashRouteGenerator(
        str(sample_osm_file),
        str(tmp_path),
        ignore_oneway=True,
        prefer_right_turns=True,
        progress_callback=progress_callback
    )
    
    # Generate route
    gpx_path, report_path = generator.generate()
    
    # Check that progress was reported
    assert len(progress_steps) > 0
    assert any(step == "complete" for step, _, _ in progress_steps)
    
    # Check output files exist
    assert Path(gpx_path).exists()
    assert Path(report_path).exists()


def test_generator_ignore_oneway(sample_osm_file, tmp_path):
    """Test generator with ignore_oneway=True (Option A)"""
    generator = TrashRouteGenerator(
        str(sample_osm_file),
        str(tmp_path),
        ignore_oneway=True
    )
    
    gpx_path, report_path = generator.generate()
    assert Path(gpx_path).exists()
    assert Path(report_path).exists()
    
    summary = generator.get_summary()
    assert "stats" in summary


def test_generator_respect_oneway(sample_osm_file, tmp_path):
    """Test generator with ignore_oneway=False (Option B)"""
    generator = TrashRouteGenerator(
        str(sample_osm_file),
        str(tmp_path),
        ignore_oneway=False
    )
    
    gpx_path, report_path = generator.generate()
    assert Path(gpx_path).exists()
    assert Path(report_path).exists()


def test_generator_start_node(sample_osm_file, tmp_path):
    """Test generator with specific start node"""
    generator = TrashRouteGenerator(
        str(sample_osm_file),
        str(tmp_path)
    )
    
    gpx_path, report_path = generator.generate(start_node=1)
    assert Path(gpx_path).exists()
    
    summary = generator.get_summary()
    assert summary["stats"]["start_node"] == 1
    assert summary["stats"]["start_node_method"] == "user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
