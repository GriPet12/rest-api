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

        total_count = Book.query.count()

        books = Book.query.limit(limit).offset(offset).all()

        base_url = request.base_url

        pagination = {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }

        if offset + limit < total_count:
            pagination["next_url"] = f"{base_url}?limit={limit}&offset={offset + limit}"
        else:
            pagination["next_url"] = None

        # Add previous_url if this isn't the first page
        if offset > 0:
            prev_offset = max(0, offset - limit)
            pagination["previous_url"] = f"{base_url}?limit={limit}&offset={prev_offset}"
        else:
            pagination["previous_url"] = None

        return jsonify({
            "books": books_schema.dump(books),
            "pagination": pagination
        })
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