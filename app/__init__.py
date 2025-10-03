from flask import Flask
from .routes import create_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    create_routes(app)
    return app