"""Main entry point for the Library Management System."""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from database.db_manager import DBManager
from library import Library
from api.routes import router, set_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lms_log.txt'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Library Management System API",
    description="A production-grade Library Management System with transactional integrity",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve templates directory
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Initialize database and library
try:
    db_manager = DBManager()
    library = Library(db_manager)
    set_library(library)
    logger.info("Library Management System initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize library: {e}")
    raise

# Include routers
app.include_router(router, prefix="/api", tags=["Library Operations"])


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Library Management System")
    library.close()


@app.get("/")
async def root():
    """Root endpoint - serve index.html."""
    return FileResponse("templates/index.html")


@app.get("/{page}")
async def serve_pages(page: str):
    """Serve HTML pages."""
    allowed_pages = ["index.html", "books.html", "members.html", "borrow.html", 
                     "returns.html", "fines.html", "analytics.html"]
    if page in allowed_pages:
        return FileResponse(f"templates/{page}")
    return {"error": "Page not found"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

