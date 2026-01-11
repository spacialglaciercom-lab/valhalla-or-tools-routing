"""FastAPI application for Trash Route API"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .routes import upload, generate, download
from .websocket import progress
from .services.progress_tracker import progress_tracker
from .utils.file_handler import FileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Trash Route API")
    logger.info(f"Port: {settings.BACKEND_PORT}")
    logger.info(f"Output directory: {settings.TRASH_ROUTE_OUTPUT_DIR}")
    logger.info(f"Max file size: {settings.MAX_FILE_SIZE_MB}MB")
    
    # Initialize file handler
    file_handler = FileHandler(
        uploads_dir=settings.uploads_dir,
        outputs_dir=settings.outputs_dir,
        max_file_size_bytes=settings.max_file_size_bytes,
        retention_hours=settings.TEMP_FILE_RETENTION_HOURS
    )
    
    # Clean up old files on startup
    cleaned = file_handler.cleanup_old_files()
    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} old job directories")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trash Route API")
    progress_tracker.cleanup_old_jobs(retention_hours=settings.TEMP_FILE_RETENTION_HOURS)


# Create FastAPI app with lifespan
app = FastAPI(
    title="Trash Collection Route API",
    description="API for generating optimized trash collection routes from OSM data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(generate.router)
app.include_router(download.router)
app.include_router(progress.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Trash Collection Route API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True
    )
