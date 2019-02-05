import connexion
from flask_cors import CORS
import os

from drift.views import v0
from drift.error import handle_http_error
from drift.exceptions import HTTPError

LOG_LEVEL = os.getenv('LOG_LEVEL', "INFO")


def create_app():
    """
    Creates the flask app, loading blueprints and the configuration.
    :return:    flask app
    :rtype:     Flask
    """
    connexion_app = connexion.App(__name__, specification_dir='openapi/')
    connexion_app.add_api('api.spec.yaml')
    flask_app = connexion_app.app
    CORS(flask_app)
    flask_app.register_blueprint(v0.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    flask_app.logger.setLevel(LOG_LEVEL)
    return connexion_app
