from flask import jsonify, request
from marshmallow import ValidationError
from models import db, Book
from schemas import BookSchema

book_schema = BookSchema()
books_schema = BookSchema(many=True)


def configure_routes(app):
    @app.route("/")
    def index():
        return jsonify({
            "List": "GET /books?limit=10&cursor=0",
            "Detail": "GET /books/{id}",
            "Create": "POST /books",
            "Delete": "DELETE /books/{id}"
        })

    @app.route("/books", methods=["GET"])
    def get_books():
        limit = request.args.get('limit', 10, type=int)
        cursor = request.args.get('cursor', 0, type=int)

        books = Book.query.filter(Book.id > cursor).order_by(Book.id).limit(limit).all()

        books_data = books_schema.dump(books)

        if books:
            next_cursor = books[-1].id
            has_more = len(books) == limit
        else:
            next_cursor = cursor
            has_more = False

        result = {
            "books": books_data,
            "next_cursor": next_cursor,
            "has_more": has_more
        }

        return jsonify(result)

    @app.route("/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        book = Book.query.get_or_404(book_id)
        return jsonify(book_schema.dump(book))

    @app.route("/books", methods=["POST"])
    def add_book():
        try:
            book_data = book_schema.load(request.get_json())
            book = Book(**book_data)
            db.session.add(book)
            db.session.commit()
            return jsonify(book_schema.dump(book)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return "", 204