from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

app = FastAPI()

books: List[Dict] = []


class Book(BaseModel):
    id: int = Field(..., gt=0, description="Унікальний ID книги")
    title: str = Field(..., min_length=1, max_length=100, description="Назва книги")
    author: str = Field(..., min_length=1, max_length=50, description="Автор книги")

@app.get("/books", response_model=List[Book])
def get_books():
    return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не знайдена")

@app.post("/books", response_model=Book)
def add_book(book: Book):
    for existing_book in books:
        if existing_book["id"] == book.id:
            raise HTTPException(status_code=400, detail="Книга з таким ID вже існує")

    books.append(book.dict())
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(index)
            return {"message": "Книга успішно видалена"}
    raise HTTPException(status_code=404, detail="Книга не знайдена")
