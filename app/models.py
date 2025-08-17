from sqlalchemy import Column, Integer, Float, String, Boolean, UniqueConstraint, event
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import validates
from slugify import slugify

from .database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    rating = Column(Float, nullable=False)
    description = Column(String)
    content_url = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)


@event.listens_for(Book, "after_insert")
def set_slug_after_insert(mapper, connection, target):
    raw_slug = slugify(target.title)
    new_slug = f"{raw_slug}-{target.id}"
    connection.execute(
        Book.__table__.update()
        .where(Book.id == target.id)
        .values(slug=new_slug)
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class UserLibrary(Base):
    __tablename__ = "user_library"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint('book_id', 'user_id', name='uq_user_id_user_id'),
    )


class BookQuestion(Base):
    __tablename__ = "book_questions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
