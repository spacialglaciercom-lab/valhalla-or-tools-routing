"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    # Set test output directory
    test_dir = Path(__file__).parent / "test_outputs"
    test_dir.mkdir(exist_ok=True)
    
    monkeypatch.setenv("TRASH_ROUTE_OUTPUT_DIR", str(test_dir))
    monkeypatch.setenv("BACKEND_PORT", "8003")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "500")
    monkeypatch.setenv("TEMP_FILE_RETENTION_HOURS", "24")
