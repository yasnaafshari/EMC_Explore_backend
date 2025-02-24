from sqlalchemy import Column, Integer, String, Enum, LargeBinary
import enum
from app.models.base import BaseModel

class FileType(enum.Enum):
    EXCEL = "excel"
    CSV = "csv"

class Dataset(BaseModel):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    
    def __repr__(self):
        return f"<Dataset(name='{self.name}', type='{self.file_type}')>" 