from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.base import BaseModel as DBBaseModel

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=DBBaseModel)
# Generic type for Pydantic schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)

class BaseRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        read_schema: Type[ReadSchemaType],
        prefix: str
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema
        
        self.router = APIRouter(prefix=f"/{prefix}", tags=[prefix])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/", response_model=self.read_schema)
        async def create(
            item: self.create_schema,
            db: Session = Depends(get_db),
            user_id: int = 1  # TODO: Get from auth token
        ):
            db_item = self.model(**item.model_dump())
            db.add(db_item)
            try:
                db.commit()
                db.refresh(db_item)
                return db_item
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.get("/", response_model=List[self.read_schema])
        async def get_all(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db),
            user_id: int = 1  # TODO: Get from auth token
        ):
            items = db.query(self.model)\
                .filter(self.model.deleted_at.is_(None))\
                .offset(skip)\
                .limit(limit)\
                .all()
            return items

        @self.router.get("/{item_id}", response_model=self.read_schema)
        async def get_one(
            item_id: int,
            db: Session = Depends(get_db),
            user_id: int = 1  # TODO: Get from auth token
        ):
            item = db.query(self.model)\
                .filter(
                    self.model.id == item_id,
                    self.model.deleted_at.is_(None)
                )\
                .first()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.put("/{item_id}", response_model=self.read_schema)
        async def update(
            item_id: int,
            item: self.update_schema,
            db: Session = Depends(get_db),
            user_id: int = 1  # TODO: Get from auth token
        ):
            db_item = db.query(self.model)\
                .filter(
                    self.model.id == item_id,
                    self.model.deleted_at.is_(None)
                )\
                .first()
            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            for key, value in item.model_dump(exclude_unset=True).items():
                setattr(db_item, key, value)
            
            try:
                db.commit()
                db.refresh(db_item)
                return db_item
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.delete("/{item_id}")
        async def delete(
            item_id: int,
            db: Session = Depends(get_db),
            user_id: int = 1  # TODO: Get from auth token
        ):
            db_item = db.query(self.model)\
                .filter(
                    self.model.id == item_id,
                    self.model.deleted_at.is_(None)
                )\
                .first()
            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            from datetime import datetime, UTC
            db_item.deleted_at = datetime.now(UTC)
            
            try:
                db.commit()
                return {"message": "Item deleted successfully"}
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e)) 