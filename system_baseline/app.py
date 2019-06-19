import logging

import connexion
from flask_migrate import Migrate

from system_baseline import config
from system_baseline.views import v0
from system_baseline.exceptions import HTTPError
from system_baseline.errors import handle_http_error
from system_baseline.models import db
from system_baseline.metrics_registry import create_prometheus_registry_dir
from system_baseline.cloudwatch import setup_cw_logging


def create_app():
    """
    Creates the app, loading blueprints and the configuration.
    :return:    app
    """
    create_prometheus_registry_dir()
    return create_connexion_app()


def create_connexion_app():
    openapi_args = {"path_prefix": config.path_prefix, "app_name": config.app_name}
    connexion_app = connexion.App(
        __name__, specification_dir="openapi/", arguments=openapi_args
    )
    connexion_app.add_api("api.spec.yaml")
    connexion_app.add_api("mgmt_api.spec.yaml")
    flask_app = connexion_app.app

    # set up logging ASAP
    gunicorn_logger = logging.getLogger("gunicorn.error")
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
    setup_cw_logging(flask_app.logger)

    # set up DB
    flask_app.config["SQLALCHEMY_ECHO"] = False
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.db_uri
    flask_app.config["SQLALCHEMY_POOL_SIZE"] = config.db_pool_size
    flask_app.config["SQLALCHEMY_POOL_TIMEOUT"] = config.db_pool_timeout
    db.init_app(flask_app)

    flask_app.register_blueprint(v0.section)
    flask_app.register_error_handler(HTTPError, handle_http_error)
    return connexion_app


def get_flask_app_with_migration():
    """
    return a Flask app. This is useful for migration code that expects a Flask
    app and not a Connexion app.
    """
    connexion_app = create_connexion_app()
    flask_app = connexion_app.app
    Migrate(flask_app, db)
    return flask_app
