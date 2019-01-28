import connexion
from flask_cors import CORS

from drift.views import v0


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
    return connexion_app
