from fastapi import FastAPI

app = FastAPI()


@app.get("/books")
async def read_all_books():
    return {"message": "All Books"}


@app.get("/books/{book_id}")
async def read_book(book_id: int):
    return {"message": f"Book {book_id}"}


@app.get("/books/")
async def search_by_title(title: str):
    return {"message": f"Book of title: {title}"}
