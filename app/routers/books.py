from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session

from ..database import Base, engine, SessionLocal
from ..models import Book

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


@router.get("", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency):
    return db.query(Book).all()


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(db: db_dependency, book_id: int = Path(gt=0)):
    record = db.query(Book).filter(Book.id == book_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


@router.get("/", status_code=status.HTTP_200_OK)
async def search_by_title(db: db_dependency, title: str):
    record = db.query(Book).filter(Book.title == title).first()
    if not record:
        raise HTTPException(status_code=404, detail="Book not found")
    return record
