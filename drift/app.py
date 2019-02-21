import connexion
import logging

from drift import config
from drift.views import v0
from drift.error import handle_http_error
from drift.exceptions import HTTPError
from drift.metrics_registry import create_prometheus_registry_dir


def create_app():
    """
    Creates the flask app, loading blueprints and the configuration.
    :return:    flask app
    :rtype:     Flask
    """
    openapi_args = {'path_prefix': config.path_prefix, 'app_name': config.app_name}
    connexion_app = connexion.App(__name__, specification_dir='openapi/', arguments=openapi_args)
    connexion_app.add_api('api.spec.yaml')
    connexion_app.add_api('mgmt_api.spec.yaml')
    flask_app = connexion_app.app

    create_prometheus_registry_dir()

    # set up logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)

    flask_app.register_blueprint(v0.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    return connexion_app
