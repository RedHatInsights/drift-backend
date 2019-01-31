import connexion
from flask_cors import CORS

from drift.views import v0
from drift.error import handle_http_error
from drift.exceptions import HTTPError


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
    return connexion_app
