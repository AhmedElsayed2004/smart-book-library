from enum import Enum

from sqlalchemy import Column, Integer, Float, String, Boolean, UniqueConstraint, event, Enum as SAEnum, DateTime, func
from sqlalchemy.sql.schema import ForeignKey
from slugify import slugify

from .database import Base


# class UserRole(Enum):
#     USER = "user"
#     ADMIN = "admin"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    rating = Column(Float, nullable=False)
    description = Column(String)
    content_url = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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
    role = Column(String, nullable=False, default='user')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserLibrary(Base):
    __tablename__ = "user_library"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('book_id', 'user_id', name='uq_user_id_user_id'),
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String, nullable=False)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
