from pydantic import BaseModel, Field, EmailStr
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

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    disabled: Optional[bool] = False

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_at: int
    refresh_token_expires_at: int

class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    disabled: Optional[bool] = False