import logging
import os

import connexion

from kerlescan import config
from kerlescan.audit_logging import setup_audit_logging
from kerlescan.cloudwatch import setup_cw_logging
from kerlescan.error import handle_http_error
from kerlescan.exceptions import HTTPError
from kerlescan.metrics_registry import create_prometheus_registry_dir

from drift.hsts_response import register_hsts_response
from drift.views import v1


def create_app():
    """
    Creates the flask app, loading blueprints and the configuration.
    :return:    flask app
    :rtype:     Flask
    """
    app_name = os.getenv("APP_NAME", "drift")
    openapi_args = {"path_prefix": config.path_prefix, "app_name": app_name}
    connexion_app = connexion.App(__name__, specification_dir="openapi/", arguments=openapi_args)
    connexion_app.add_api("api.spec.yaml", validate_responses=True, strict_validation=True)
    connexion_app.add_api("mgmt_api.spec.yaml")
    connexion_app.add_api("admin_api.spec.yaml", validate_responses=True, strict_validation=True)
    flask_app = connexion_app.app

    create_prometheus_registry_dir()

    # set up logging
    setup_audit_logging()

    register_hsts_response(flask_app)

    gunicorn_logger = logging.getLogger("gunicorn.error")
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
    setup_cw_logging(
        flask_app.logger, logging.getLogger("gunicorn.access"), logging.getLogger("gunicorn.error")
    )

    flask_app.register_blueprint(v1.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    return connexion_app
