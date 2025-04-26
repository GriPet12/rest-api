from flask_restful import Api, Resource
from flask_apispec import FlaskApiSpec, doc, use_kwargs, marshal_with
from marshmallow import fields
from models import db, Book
from schemas import BookSchema

book_schema = BookSchema()
books_schema = BookSchema(many=True)

class BookListResource(Resource):
    @doc(description="Get a list of books", tags=["Books"])
    @use_kwargs({"limit": fields.Int(missing=10), "cursor": fields.Int(missing=0)}, location="query")
    @marshal_with({"books": fields.List(fields.Nested(BookSchema)), "next_cursor": fields.Int, "has_more": fields.Bool})
    def get(self, limit, cursor):
        books = Book.query.filter(Book.id > cursor).order_by(Book.id).limit(limit).all()
        books_data = books_schema.dump(books)
        next_cursor = books[-1].id if books else cursor
        has_more = len(books) == limit
        return {"books": books_data, "next_cursor": next_cursor, "has_more": has_more}

    @doc(description="Add a new book", tags=["Books"])
    @use_kwargs(BookSchema, location="json")
    @marshal_with(BookSchema, code=201)
    def post(self, **kwargs):
        book = Book(**kwargs)
        db.session.add(book)
        db.session.commit()
        return book, 201

class BookResource(Resource):
    @doc(description="Get a book by ID", tags=["Books"])
    @marshal_with(BookSchema)
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return book

    @doc(description="Delete a book by ID", tags=["Books"])
    def delete(self, book_id):
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return "", 204

def configure_routes(app):
    api = Api(app)
    api.add_resource(BookListResource, "/books")
    api.add_resource(BookResource, "/books/<int:book_id>")