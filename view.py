from flask import jsonify, request
from marshmallow import ValidationError
from schemas import BookSchema

books = [
    {"id": 1, "title": "Крах Людини", "author": "Осаму Дадзая"},
    {"id": 2, "title": "1984", "author": "Джордж Оруелл"},
    {"id": 3, "title": "Володар перснів", "author": "Джон Р. Р. Толкін"},
]

book_schema = BookSchema()
books_schema = BookSchema(many=True)


def configure_routes(app):
    @app.route("/")
    def index():
        return jsonify({"List": "GET /books",
                        "Detail": "GET /books/{id}",
                        "Create": "POST /books",
                        "Delete": "DELETE /books/{id}"})

    @app.route("/books", methods=["GET"])
    def get_books():
        return jsonify(books_schema.dump(books))

    @app.route("/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        book = next((book for book in books if book["id"] == book_id), None)
        if book:
            return jsonify(book_schema.dump(book))
        return jsonify({"message": "Книга не знайдена"}), 404

    @app.route("/books", methods=["POST"])
    def add_book():
        try:
            book = book_schema.load(request.get_json())
            book["id"] = max(book["id"] for book in books) + 1 if books else 1
            books.append(book)
            return jsonify(book_schema.dump(book)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        global books
        books = [book for book in books if book["id"] != book_id]
        return jsonify({"message": "Книга видалена"}), 204