from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .auth import get_current_user
from ..database import SessionLocal
from ..models import Book

from ..services import ai_service






router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency):
    return db.query(Book).all()


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(db: db_dependency, book_id: int = Path(gt=0)):
    record = db.query(Book).filter(Book.id == book_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


@router.get("/", status_code=status.HTTP_200_OK)
async def search_by_title(db: db_dependency, title: str):
    record = db.query(Book).filter(Book.title == title).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


