from pydantic import BaseModel, Field
from typing import List, Optional

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Назва книги")
    author: str = Field(..., min_length=1, max_length=50, description="Автор книги")


class Book(BookCreate):
    id: int = Field(..., gt=0, description="Унікальний ID книги")


class BooksResponse(BaseModel):
    items: List[Book]
    next_cursor: Optional[int] = None
    total: int