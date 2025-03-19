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
            "List": "GET /books?limit=10&offset=0",
            "Detail": "GET /books/{id}",
            "Create": "POST /books",
            "Delete": "DELETE /books/{id}"
        })

    @app.route("/books", methods=["GET"])
    def get_books():
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)

        books = Book.query.limit(limit).offset(offset).all()
        return jsonify(books_schema.dump(books))

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