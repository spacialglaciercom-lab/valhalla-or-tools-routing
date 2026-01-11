"""
Integration tests for Trash Route API
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory and backend directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "trash-route-api"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_osm_file(temp_dir):
    """Create a sample OSM XML file for testing"""
    osm_content = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="37.7749" lon="-122.4194"/>
  <node id="2" lat="37.7750" lon="-122.4195"/>
  <node id="3" lat="37.7751" lon="-122.4196"/>
  <way id="1">
    <nd ref="1"/>
    <nd ref="2"/>
    <nd ref="3"/>
    <tag k="highway" v="residential"/>
  </way>
</osm>
"""
    osm_path = Path(temp_dir) / "test.osm"
    osm_path.write_text(osm_content)
    return osm_path


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Trash Collection Route API"
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_upload_osm_file(sample_osm_file):
    """Test OSM file upload"""
    with open(sample_osm_file, "rb") as f:
        response = client.post(
            "/api/trash-route/upload",
            files={"file": ("test.osm", f, "application/xml")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "upload_id" in data
    assert data["filename"] == "test.osm"
    assert data["file_size"] > 0


def test_upload_invalid_file():
    """Test upload with invalid file format"""
    response = client.post(
        "/api/trash-route/upload",
        files={"file": ("test.txt", b"invalid content", "text/plain")}
    )
    assert response.status_code == 400


def test_generate_route(sample_osm_file):
    """Test route generation"""
    # First upload file
    with open(sample_osm_file, "rb") as f:
        upload_response = client.post(
            "/api/trash-route/upload",
            files={"file": ("test.osm", f, "application/xml")}
        )
    upload_id = upload_response.json()["upload_id"]
    
    # Generate route
    generate_request = {
        "upload_id": upload_id,
        "config": {
            "ignore_oneway": True,
            "highway_include": ["residential", "unclassified"],
            "excluded_conditions": [],
            "prefer_right_turns": True
        }
    }
    
    response = client.post(
        "/api/trash-route/generate",
        json=generate_request
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["pending", "processing"]


def test_get_job_status(sample_osm_file):
    """Test getting job status"""
    # First upload file
    with open(sample_osm_file, "rb") as f:
        upload_response = client.post(
            "/api/trash-route/upload",
            files={"file": ("test.osm", f, "application/xml")}
        )
    upload_id = upload_response.json()["upload_id"]
    
    # Generate route
    generate_request = {
        "upload_id": upload_id,
        "config": {
            "ignore_oneway": True,
            "highway_include": ["residential", "unclassified"],
            "excluded_conditions": [],
            "prefer_right_turns": True
        }
    }
    
    generate_response = client.post(
        "/api/trash-route/generate",
        json=generate_request
    )
    
    assert generate_response.status_code == 200
    job_id = generate_response.json()["job_id"]
    
    # Get status
    response = client.get(f"/api/trash-route/status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data


def test_get_nonexistent_job_status():
    """Test getting status for non-existent job"""
    response = client.get("/api/trash-route/status/nonexistent-job-id")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
