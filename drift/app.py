from flask import Flask
from flask_cors import CORS

from drift.views import v0


def create_app():
    """
    Creates the flask app, loading blueprints and the configuration.
    :return:    flask app
    :rtype:     Flask
    """
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(v0.section)
    return app
