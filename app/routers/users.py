from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .auth import get_current_user
from ..database import SessionLocal
from sqlalchemy.orm import Session

from ..models import Book, UserLibrary


class BooKRequest(BaseModel):
    book_id: int = Field(gt=0)


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# need auth
@router.get("/me/library", status_code=status.HTTP_200_OK)
async def get_library_books(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id = user.get('id')
    library_books = db.query(UserLibrary).filter(UserLibrary.user_id == user_id).all()
    return library_books


# need auth
@router.post("/me/library", status_code=status.HTTP_201_CREATED)
async def add_book_to_library(user: user_dependency, book_request: BooKRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id = user.get('id')
    book_id = book_request.book_id
    if db.query(Book).filter(Book.id == book_id).first() is None:
        raise HTTPException(status_code=404, detail="Added Book not found")
    book = UserLibrary(book_id=book_id, user_id=user_id)
    db.add(book)
    db.commit()


@router.delete("/me/library/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book_from_library(user: user_dependency, book_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id = user.get('id')
    book_id = book_id
    book = db.query(UserLibrary).filter(UserLibrary.book_id == book_id).filter(UserLibrary.user_id == user_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
