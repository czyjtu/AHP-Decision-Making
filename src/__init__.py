from flask import Flask
from src.routes import ahp_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(ahp_blueprint)
    return app

