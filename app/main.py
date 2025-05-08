from fastapi import FastAPI

from app.database import db
from app.routers import books, auth

app = FastAPI(title="Library API")

app.include_router(auth.router)
app.include_router(books.router)

@app.on_event("startup")
async def startup():
    await db.connect_to_database()

@app.on_event("shutdown")
async def shutdown():
    await db.close_database_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to Library API"}