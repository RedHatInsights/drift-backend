import logging

import connexion

from flask_migrate import Migrate
from kerlescan import config as kerlescan_config
from kerlescan.audit_logging import setup_audit_logging
from kerlescan.cloudwatch import setup_cw_logging
from kerlescan.error import handle_http_error
from kerlescan.exceptions import HTTPError
from kerlescan.metrics_registry import create_prometheus_registry_dir

from historical_system_profiles import app_config, config
from historical_system_profiles.hsts_response import register_hsts_response
from historical_system_profiles.models import db
from historical_system_profiles.views import v1


def create_app():
    """
    Creates the app, loading blueprints and the configuration.
    :return:    app
    """
    create_prometheus_registry_dir()
    return create_connexion_app()


def create_connexion_app():
    openapi_args = {
        "path_prefix": kerlescan_config.path_prefix,
        "app_name": app_config.get_app_name(),
    }
    connexion_app = connexion.App(__name__, specification_dir="openapi/", arguments=openapi_args)
    connexion_app.add_api("api.spec.yaml", strict_validation=True, validate_responses=True)
    connexion_app.add_api("mgmt_api.spec.yaml", strict_validation=True)
    flask_app = connexion_app.app

    # set up logging ASAP
    setup_audit_logging(logging.Logger)

    gunicorn_logger = logging.getLogger("gunicorn.error")
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
    setup_cw_logging(flask_app.logger, logging.getLogger("gunicorn.access"), gunicorn_logger)
    register_hsts_response(flask_app)

    # set up DB
    engine_options = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": config.db_pool_size,
        "pool_timeout": config.db_pool_timeout,
    }
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.db_uri
    flask_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options

    flask_app.config["SQLALCHEMY_ECHO"] = False
    if config.log_sql_statements:
        flask_app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(flask_app)

    flask_app.register_blueprint(v1.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    return connexion_app


def get_flask_app_with_migration():  # pragma: no cover
    """
    return a Flask app. This is useful for migration code that expects a Flask
    app and not a Connexion app.
    """
    connexion_app = create_connexion_app()
    flask_app = connexion_app.app
    Migrate(flask_app, db)
    return flask_app
