import logging

import connexion

from kerlescan.metrics_registry import create_prometheus_registry_dir
from kerlescan import config
from kerlescan.cloudwatch import setup_cw_logging
from kerlescan.exceptions import HTTPError
from kerlescan.error import handle_http_error

from historical_system_profiles import app_config
from historical_system_profiles.views import v0


def create_app():
    """
    Creates the app, loading blueprints and the configuration.
    :return:    app
    """
    create_prometheus_registry_dir()
    return create_connexion_app()


def create_connexion_app():
    openapi_args = {
        "path_prefix": config.path_prefix,
        "app_name": app_config.get_app_name(),
    }
    connexion_app = connexion.App(
        __name__, specification_dir="openapi/", arguments=openapi_args
    )
    connexion_app.add_api(
        "api.spec.yaml", strict_validation=True, validate_responses=True
    )
    flask_app = connexion_app.app

    # set up logging ASAP
    gunicorn_logger = logging.getLogger("gunicorn.error")
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
    setup_cw_logging(flask_app.logger)

    flask_app.register_blueprint(v0.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    return connexion_app
