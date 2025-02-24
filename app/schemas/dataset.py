from datetime import datetime
from app.models.dataset import FileType
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema

class DatasetCreate(BaseCreateSchema):
    name: str
    file_type: FileType

class DatasetUpdate(BaseUpdateSchema):
    name: str | None = None

class DatasetRead(BaseSchema):
    name: str
    file_type: FileType

class Dataset(BaseSchema):
    id: int
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True 