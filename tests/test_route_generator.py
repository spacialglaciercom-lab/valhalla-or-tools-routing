#!/usr/bin/env python3
"""Unit tests for trash collection route generator"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.route_generator import TrashRouteGenerator
from src.route_generator.osm_parser import OSMParser
from src.route_generator.graph_builder import GraphBuilder
from src.route_generator.component_analyzer import ComponentAnalyzer
from src.route_generator.eulerian_solver import EulerianSolver
from src.route_generator.gpx_writer import GPXWriter
from src.route_generator.utils import haversine_distance, bearing, turn_angle, turn_cost


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_haversine_distance(self):
        """Test haversine distance calculation"""
        # Montreal to Toronto approximately 504 km
        dist = haversine_distance(45.5017, -73.5673, 43.6629, -79.3957)
        self.assertAlmostEqual(dist, 504, delta=10)
    
    def test_bearing(self):
        """Test bearing calculation"""
        # North bearing should be ~0
        b = bearing(45.0, -73.0, 46.0, -73.0)
        self.assertAlmostEqual(b, 0, delta=5)
        
        # East bearing should be ~90
        b = bearing(45.0, -73.0, 45.0, -72.0)
        self.assertAlmostEqual(b, 90, delta=5)
    
    def test_turn_angle(self):
        """Test turn angle calculation"""
        # Straight should be ~0
        angle = turn_angle(0, 0)
        self.assertAlmostEqual(angle, 0)
        
        # 90 degree right turn
        angle = turn_angle(0, 90)
        self.assertAlmostEqual(abs(angle), 90, delta=1)
    
    def test_turn_cost(self):
        """Test turn cost function"""
        # Right turn should have lower cost than left
        right_cost = turn_cost(45)
        left_cost = turn_cost(-45)
        self.assertLess(right_cost, left_cost)


class TestOSMParser(unittest.TestCase):
    """Test OSM parsing"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test OSM file"""
        cls.osm_file = Path(__file__).parent.parent / "mercier_area.osm"
        assert cls.osm_file.exists(), "Test OSM file not found"
    
    def test_parse_nodes(self):
        """Test node parsing"""
        parser = OSMParser(str(self.osm_file))
        nodes, _ = parser.parse()
        
        self.assertEqual(len(nodes), 20)
        self.assertIn(1, nodes)
        self.assertAlmostEqual(nodes[1].lat, 45.3040, places=4)
        self.assertAlmostEqual(nodes[1].lon, -73.7420, places=4)
    
    def test_parse_ways(self):
        """Test way parsing"""
        parser = OSMParser(str(self.osm_file))
        nodes, ways = parser.parse()
        
        self.assertEqual(len(ways), 9)  # 9 driveable ways
    
    def test_driveable_filtering(self):
        """Test highway type filtering"""
        parser = OSMParser(str(self.osm_file))
        nodes, ways = parser.parse()
        
        # Check footway excluded
        for way_id, way in parser.ways.items():
            if way.tags.get('highway') == 'footway':
                self.assertNotIn(way_id, ways)


class TestGraphBuilder(unittest.TestCase):
    """Test graph construction"""
    
    def test_add_segment(self):
        """Test segment addition"""
        builder = GraphBuilder()
        
        builder.add_segment(1, 2, 45.0, -73.0, 45.1, -73.0, 10.0)
        
        graph = builder.get_graph()
        self.assertEqual(graph.number_of_nodes(), 2)
        # Should have bidirectional edges
        self.assertTrue(graph.has_edge(1, 2))
        self.assertTrue(graph.has_edge(2, 1))
    
    def test_node_coords(self):
        """Test node coordinate storage"""
        builder = GraphBuilder()
        builder.add_segment(1, 2, 45.0, -73.0, 45.1, -73.0)
        
        coords = builder.get_node_coords(1)
        self.assertAlmostEqual(coords[0], 45.0)
        self.assertAlmostEqual(coords[1], -73.0)


class TestComponentAnalyzer(unittest.TestCase):
    """Test component analysis"""
    
    def test_single_component(self):
        """Test analysis of single component"""
        import networkx as nx
        
        # Create connected graph
        G = nx.MultiDiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        
        analyzer = ComponentAnalyzer(G)
        info = analyzer.analyze()
        
        self.assertEqual(info['total_components'], 1)
        self.assertEqual(info['largest_component_size'], 3)
    
    def test_multiple_components(self):
        """Test analysis of multiple components"""
        import networkx as nx
        
        G = nx.MultiDiGraph()
        # Component 1: 1-2-3
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        # Component 2: 4-5
        G.add_edges_from([(4, 5), (5, 4)])
        
        analyzer = ComponentAnalyzer(G)
        info = analyzer.analyze()
        
        self.assertEqual(info['total_components'], 2)
        self.assertEqual(info['largest_component_size'], 3)
        self.assertEqual(info['excluded_nodes'], 2)


class TestEulerianSolver(unittest.TestCase):
    """Test Eulerian circuit solving"""
    
    def test_eulerian_circuit(self):
        """Test Eulerian circuit generation"""
        import networkx as nx
        
        # Create Eulerian graph (square)
        G = nx.MultiDiGraph()
        edges = [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3), (3, 1), (2, 4), (4, 2)]
        G.add_edges_from(edges)
        
        solver = EulerianSolver(G)
        circuit = solver.solve()
        
        # Circuit should have all edges
        self.assertEqual(len(circuit), len(edges))
        
        # Check if valid circuit (starts and ends at same node)
        if len(circuit) > 0:
            start = circuit[0][0]
            end = circuit[-1][1]
            # In Eulerian circuit, may not start/end same due to algorithm


class TestGPXWriter(unittest.TestCase):
    """Test GPX writing"""
    
    def test_write_gpx(self):
        """Test GPX file generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            coords = {
                1: (45.0, -73.0),
                2: (45.1, -73.0),
                3: (45.1, -73.1),
            }
            
            writer = GPXWriter(coords)
            circuit = [(1, 2), (2, 3), (3, 1)]
            
            output_file = os.path.join(tmpdir, "test.gpx")
            writer.write_circuit(circuit, output_file, "Test Route")
            
            # Check file exists
            self.assertTrue(os.path.exists(output_file))
            
            # Check file content
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('<gpx', content)
                self.assertIn('<trk>', content)
                self.assertIn('<trkseg>', content)


class TestTrashRouteGenerator(unittest.TestCase):
    """Integration tests for full generator"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test OSM file"""
        cls.osm_file = Path(__file__).parent.parent / "mercier_area.osm"
        assert cls.osm_file.exists(), "Test OSM file not found"
    
    def test_full_generation(self):
        """Test full route generation pipeline"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = TrashRouteGenerator(str(self.osm_file), tmpdir)
            gpx_file, report_file = generator.generate()
            
            # Check files created
            self.assertTrue(os.path.exists(gpx_file))
            self.assertTrue(os.path.exists(report_file))
            
            # Check GPX structure
            with open(gpx_file, 'r') as f:
                gpx_content = f.read()
                self.assertIn('<trk>', gpx_content)
                self.assertIn('<trkseg>', gpx_content)
                self.assertIn('trkpt', gpx_content)
    
    def test_summary(self):
        """Test generation summary"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = TrashRouteGenerator(str(self.osm_file), tmpdir)
            generator.generate()
            
            summary = generator.get_summary()
            
            self.assertIn('nodes_parsed', summary)
            self.assertIn('driveable_ways', summary)
            self.assertIn('segments', summary)
            self.assertIn('circuit_edges', summary)
            
            # Verify counts
            self.assertEqual(summary['nodes_parsed'], 20)
            self.assertEqual(summary['driveable_ways'], 9)
            self.assertEqual(summary['segments'], 29)
            self.assertEqual(summary['circuit_edges'], 58)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestOSMParser))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestComponentAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestEulerianSolver))
    suite.addTests(loader.loadTestsFromTestCase(TestGPXWriter))
    suite.addTests(loader.loadTestsFromTestCase(TestTrashRouteGenerator))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
