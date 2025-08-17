from typing import Annotated
from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import Base, engine, SessionLocal
from ..models import Book

from ..services import ai_service


class AskAIRequest(BaseModel):
    question: str


class BookRequest(BaseModel):
    author: str = Field(min_length=1)
    title: str = Field(min_length=1)
    rating: float = Field(gt=0, lt=5)
    description: str | None
    content_url: str


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
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


@router.get("/", status_code=status.HTTP_200_OK)
async def search_by_title(db: db_dependency, title: str):
    record = db.query(Book).filter(Book.title == title).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


@router.post("/{book_id}/ask")
async def ask_about_book(db: db_dependency, ask_ai_request: AskAIRequest, book_id: int = Path(gt=0)):
    record: Book | None = db.query(Book).filter(Book.id == book_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    question = ask_ai_request.question
    answer = ai_service.answer_about_book(question, record.slug)
    return {"answer": answer}


@router.post("")
async def create_book(db: db_dependency, book: BookRequest):
    record = Book(**book.model_dump())
    db.add(record)
    db.commit()
