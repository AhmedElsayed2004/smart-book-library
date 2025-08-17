from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import Float

from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    description = Column(String)
    content_url = Column(String, nullable=False)
