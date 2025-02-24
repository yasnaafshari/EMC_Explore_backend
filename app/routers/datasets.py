from fastapi import UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.database import get_db
from app.models.dataset import Dataset, FileType
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetRead
from app.services.dataset import DatasetService
from app.routers.base import BaseRouter
from app.config import settings

dataset_service = DatasetService()

base_router = BaseRouter[Dataset, DatasetCreate, DatasetUpdate, DatasetRead](
    model=Dataset,
    create_schema=DatasetCreate,
    update_schema=DatasetUpdate,
    read_schema=DatasetRead,
    prefix="datasets"
)

router = base_router.router

def determine_file_type(filename: str) -> Optional[FileType]:
    extension = filename.lower().split('.')[-1]
    if extension == 'csv':
        return FileType.CSV
    elif extension in ['xls', 'xlsx']:
        return FileType.EXCEL
    return None


@router.get("/{dataset_id}/download")
async def download_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset = dataset_service.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    extension = ".xlsx" if dataset.file_type == FileType.EXCEL else ".csv"
    filename = f"{dataset.name}{extension}"

    return StreamingResponse(
        BytesIO(dataset.file_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/", response_model=DatasetRead)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> DatasetRead:
    extension = file.filename.lower().split('.')[-1]
    if extension not in ['csv', 'xls', 'xlsx']:
        raise HTTPException(
            status_code=400,
            detail="File type not supported. Please upload CSV or Excel files only."
        )
    
    file_type = FileType.CSV if extension == 'csv' else FileType.EXCEL
    file_content = await file.read()
    
    dataset_service = DatasetService(db)
    dataset = dataset_service.create_dataset(
        name=file.filename,
        file_content=file_content,
        file_type=file_type
    )
    
    return dataset

@router.get("/", response_model=List[DatasetRead])
def get_datasets(
    db: Session = Depends(get_db)
) -> List[DatasetRead]:
    dataset_service = DatasetService(db)
    return dataset_service.get_datasets() 