from fastapi import APIRouter, HTTPException, Query, Depends

from app.models import Book, BookCreate, BooksResponse
from app.database import get_collection

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=BooksResponse)
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


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, collection=Depends(get_collection)):
    book = await collection.find_one({"id": book_id})
    if book:
        book.pop('_id', None)
        return book
    raise HTTPException(status_code=404, detail="Книга не знайдена")


@router.post("", response_model=Book)
async def add_book(book: BookCreate, collection=Depends(get_collection)):
    last_book = await collection.find_one({}, sort=[("id", -1)])
    new_id = 1 if not last_book else last_book["id"] + 1

    book_dict = book.model_dump()
    book_dict["id"] = new_id

    await collection.insert_one(book_dict)
    return book_dict


@router.delete("/{book_id}")
async def delete_book(book_id: int, collection=Depends(get_collection)):
    result = await collection.delete_one({"id": book_id})
    if result.deleted_count:
        return {"message": "Книга успішно видалена"}
    raise HTTPException(status_code=404, detail="Книга не знайдена")