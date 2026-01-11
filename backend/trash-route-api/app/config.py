"""Configuration for Trash Route API"""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings"""
    
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8003"))
    TRASH_ROUTE_OUTPUT_DIR: str = os.getenv("TRASH_ROUTE_OUTPUT_DIR", "D:/trash_routes")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    TEMP_FILE_RETENTION_HOURS: int = int(os.getenv("TEMP_FILE_RETENTION_HOURS", "24"))
    PYTHON_PATH: str = os.getenv("PYTHON_PATH", os.getcwd())
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]
    
    def __init__(self):
        """Initialize and validate settings"""
        # Ensure output directory exists
        Path(self.TRASH_ROUTE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        Path(self.outputs_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def uploads_dir(self) -> str:
        """Get uploads directory path"""
        return str(Path(self.TRASH_ROUTE_OUTPUT_DIR) / "uploads")
    
    @property
    def outputs_dir(self) -> str:
        """Get outputs directory path"""
        return str(Path(self.TRASH_ROUTE_OUTPUT_DIR) / "outputs")
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
