from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, UTC
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model)\
            .filter(self.model.deleted_at.is_(None))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create(self, db: Session, data: dict) -> ModelType:
        try:
            db_item = self.model(**data)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Could not create {self.model.__name__}: {str(e)}"
            )

    def update(
        self,
        db: Session,
        id: int,
        data: dict
    ) -> Optional[ModelType]:
        try:
            db_item = self.get_by_id(db, id)
            if not db_item:
                return None

            for key, value in data.items():
                if hasattr(db_item, key):
                    setattr(db_item, key, value)

            db.commit()
            db.refresh(db_item)
            return db_item
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Could not update {self.model.__name__}: {str(e)}"
            )

    def delete(self, db: Session, id: int) -> bool:
        try:
            db_item = self.get_by_id(db, id)
            if not db_item:
                return False

            db_item.deleted_at = datetime.now(UTC)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Could not delete {self.model.__name__}: {str(e)}"
            )

    def exists(self, db: Session, id: int) -> bool:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first() is not None 