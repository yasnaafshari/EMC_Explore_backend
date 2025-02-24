from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime
from typing import Optional

class BaseSchema(PydanticBaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BaseCreateSchema(PydanticBaseModel):
    class Config:
        from_attributes = True

class BaseUpdateSchema(PydanticBaseModel):
    class Config:
        from_attributes = True 