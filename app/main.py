from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .routers import books, users, ai, admin, auth, sessions
from .database import Base, engine, SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(books.router)
app.include_router(users.router)
app.include_router(ai.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(sessions.router)
