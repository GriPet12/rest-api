from flask import Flask
from models import db
from view import configure_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
configure_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)