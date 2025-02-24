from fastapi import FastAPI
from sqlalchemy.orm import Session
from typing import Optional
import os
from app.models.dataset import FileType
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import datasets

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    application = FastAPI(
        title="EMC Explore API",
        version="1.0.0"
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        datasets.router,
        prefix="/api/v1",
        tags=["datasets"]
    )

    return application

app = create_application()

def determine_file_type(filename: str) -> Optional[FileType]:
    extension = filename.lower().split('.')[-1]
    if extension == 'csv':
        return FileType.CSV
    elif extension in ['xls', 'xlsx']:
        return FileType.EXCEL
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 
