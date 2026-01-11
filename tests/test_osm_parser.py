"""
Unit tests for OSM Parser
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.route_generator.osm_parser import OSMParser


@pytest.fixture
def sample_osm_file():
    """Create a sample OSM XML file"""
    osm_content = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="37.7749" lon="-122.4194"/>
  <node id="2" lat="37.7750" lon="-122.4195"/>
  <node id="3" lat="37.7751" lon="-122.4196"/>
  <way id="1">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="residential"/>
    <tag k="oneway" v="yes"/>
  </way>
  <way id="2">
    <nd ref="2"/>
    <nd ref="3"/>
    <tag k="highway" v="residential"/>
    <tag k="oneway" v="no"/>
  </way>
  <way id="3">
    <nd ref="1"/>
    <nd ref="3"/>
    <tag k="highway" v="footway"/>
  </way>
</osm>
"""
    temp_dir = tempfile.mkdtemp()
    osm_path = Path(temp_dir) / "test.osm"
    osm_path.write_text(osm_content)
    yield osm_path
    shutil.rmtree(temp_dir) if Path(temp_dir).exists() else None


def test_parser_detects_xml_format(sample_osm_file):
    """Test that parser detects XML format"""
    parser = OSMParser(str(sample_osm_file))
    assert parser.file_format == "xml"


def test_parser_parse_nodes(sample_osm_file):
    """Test parsing OSM nodes"""
    parser = OSMParser(str(sample_osm_file))
    nodes, ways = parser.parse()
    
    assert len(nodes) >= 3
    assert 1 in nodes
    assert 2 in nodes
    assert 3 in nodes
    
    # Check coordinates
    assert nodes[1].lat == 37.7749
    assert nodes[1].lon == -122.4194


def test_parser_parse_driveable_ways(sample_osm_file):
    """Test parsing driveable ways"""
    parser = OSMParser(str(sample_osm_file))
    nodes, ways = parser.parse()
    
    # Should have driveable ways (residential highways)
    # footway should be excluded
    assert len(ways) >= 2
    assert 1 in ways  # residential
    assert 2 in ways  # residential
    assert 3 not in ways  # footway excluded


def test_parser_get_oneway_tag(sample_osm_file):
    """Test getting oneway tag from ways"""
    parser = OSMParser(str(sample_osm_file))
    parser.parse()
    
    assert parser.get_way_oneway(1) == "yes"
    assert parser.get_way_oneway(2) == "no"


def test_parser_get_road_segments(sample_osm_file):
    """Test extracting road segments"""
    parser = OSMParser(str(sample_osm_file))
    parser.parse()
    
    segments = parser.get_road_segments()
    assert len(segments) > 0
    
    # Check segment format (should include oneway tag)
    first_segment = segments[0]
    assert len(first_segment) == 7  # node1, node2, lat1, lon1, lat2, lon2, oneway
    assert first_segment[6] in ["yes", "no", ""]  # oneway tag


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
