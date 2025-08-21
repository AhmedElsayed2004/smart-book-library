from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status

from ..database import SessionLocal
from ..models import Book
from .auth import get_current_user
from ..tasks import ai_tasks, book_tasks
from ..services import ai_service


class BookRequest(BaseModel):
    author: str = Field(min_length=1)
    title: str = Field(min_length=1)
    rating: float = Field(gt=0, lt=5)
    description: str | None
    content_url: str


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/books")
async def create_book(user: user_dependency, db: db_dependency, book_request: BookRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    if not user.get('role') == 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")

    record = Book(**book_request.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    #long task
    # ai_tasks.embed_book_task.delay(record.content_url, record.slug)

    try:
        result = ai_tasks.embed_book_task.delay(record.content_url, record.slug)
        print(f"Task queued successfully with ID: {result.id}")
        print(f"Task status: {result.status}")
    except Exception as e:
        print(f"Error queuing task: {e}")

    return {"message": "Adding book"}


@router.put("/books/{book_id}")
async def update_book(user: user_dependency, db: db_dependency, book_id: int, book_request: BookRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    if not user.get('role') == 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")

    record = db.query(Book).filter(Book.id == book_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    record.author = book_request.author
    record.title = book_request.title
    record.rating = book_request.rating
    record.description = book_request.description
    record.content_url = book_request.content_url
    db.commit()


@router.delete("/books/{book_id}")
async def delete_book(user: user_dependency, db: db_dependency, book_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    if not user.get('role') == 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")

    record = db.query(Book).filter(Book.id == book_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(record)
    db.commit()

    # book_tasks.delete_book_embedding.delay(record.content_url, record.slug)

    return {"message": f"Book deleted"}
