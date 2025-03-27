from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "library")
COLLECTION_NAME = "books"

class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(MONGO_URL)

    async def close_database_connection(self):
        if self.client is not None:
            self.client.close()


db = Database()


@app.on_event("startup")
async def startup():
    await db.connect_to_database()


@app.on_event("shutdown")
async def shutdown():
    await db.close_database_connection()


async def get_collection():
    return db.client[DB_NAME][COLLECTION_NAME]


class Book(BaseModel):
    id: int = Field(..., gt=0, description="Унікальний ID книги")
    title: str = Field(..., min_length=1, max_length=100, description="Назва книги")
    author: str = Field(..., min_length=1, max_length=50, description="Автор книги")


class BooksResponse(BaseModel):
    items: List[Book]
    next_cursor: Optional[int] = None
    total: int


@app.get("/books", response_model=BooksResponse)
async def get_books(
        limit: int = Query(10, ge=1, le=100),
        cursor: int = Query(0, ge=0),
        collection=Depends(get_collection)
):
    total = await collection.count_documents({})

    books_cursor = collection.find({}).skip(cursor).limit(limit + 1)
    books = await books_cursor.to_list(length=limit + 1)

    has_more = len(books) > limit
    items = books[:limit]

    next_cursor = cursor + limit if has_more else None

    for book in items:
        book.pop('_id', None)

    return {
        "items": items,
        "next_cursor": next_cursor,
        "total": total
    }


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, collection=Depends(get_collection)):
    book = await collection.find_one({"id": book_id})
    if book:
        book.pop('_id', None)
        return book
    raise HTTPException(status_code=404, detail="Книга не знайдена")


@app.post("/books", response_model=Book)
async def add_book(book: Book, collection=Depends(get_collection)):
    existing_book = await collection.find_one({"id": book.id})
    if existing_book:
        raise HTTPException(status_code=400, detail="Книга з таким ID вже існує")

    book_dict = book.model_dump()
    await collection.insert_one(book_dict)
    return book_dict


@app.delete("/books/{book_id}")
async def delete_book(book_id: int, collection=Depends(get_collection)):
    result = await collection.delete_one({"id": book_id})
    if result.deleted_count:
        return {"message": "Книга успішно видалена"}
    raise HTTPException(status_code=404, detail="Книга не знайдена")