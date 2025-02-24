from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.dataset import Dataset, FileType
from app.services.base import BaseService

class DatasetService(BaseService[Dataset]):
    def __init__(self):
        super().__init__(Dataset)

    def determine_file_type(self, filename: str) -> Optional[FileType]:
        extension = filename.lower().split('.')[-1]
        if extension == 'csv':
            return FileType.CSV
        elif extension in ['xls', 'xlsx']:
            return FileType.EXCEL
        return None

    async def create_with_file(
        self,
        db: Session,
        file: UploadFile,
        name: Optional[str] = None
    ) -> Dataset:
        # Validate file type
        file_type = self.determine_file_type(file.filename)
        if not file_type:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only CSV and Excel files are allowed."
            )
        
        dataset_name = name or file.filename.rsplit('.', 1)[0]
        
        try:
            # Read file content
            file_content = await file.read()
            
            return self.create(db, {
                "name": dataset_name,
                "file_content": file_content,
                "file_type": file_type
            })
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload dataset: {str(e)}"
            ) 