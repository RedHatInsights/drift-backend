import logging
import os

from kerlescan.config import str_to_bool

# pull the app name from the env var; we are not fully initialized yet
app_name = os.getenv("APP_NAME", "historical-system-profiles")
logger = logging.getLogger(app_name)


def get_namespace():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read()
        return namespace
    except EnvironmentError:
        logger.info("Not running in openshift")


# please ensure these are all documented in README.md
_db_user = os.getenv("HSP_DB_USER", "insights")
_db_password = os.getenv("HSP_DB_PASS", "insights")
_db_host = os.getenv("HSP_DB_HOST", "localhost:5432")
_db_name = os.getenv("HSP_DB_NAME", "insights")

db_uri = f"postgresql://{_db_user}:{_db_password}@{_db_host}/{_db_name}"
db_pool_timeout = int(os.getenv("HSP_DB_POOL_TIMEOUT", "5"))
db_pool_size = int(os.getenv("HSP_DB_POOL_SIZE", "5"))

bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "kafka:29092").split(",")
consume_topic = os.getenv("CONSUME_TOPIC", None)
group_id = os.getenv("GROUP_ID", None)
listener_type = os.getenv("LISTENER_TYPE", "ARCHIVER")

# logging params used outside of flask
aws_access_key_id = os.getenv("CW_AWS_ACCESS_KEY_ID", None)
aws_secret_access_key = os.getenv("CW_AWS_SECRET_ACCESS_KEY", None)
aws_region_name = os.getenv("CW_AWS_REGION_NAME", "us-east-1")
log_group = os.getenv("CW_LOG_GROUP", "platform-dev")
log_sql_statements = str_to_bool(os.getenv("LOG_SQL_STATEMENTS", "False"))
namespace = get_namespace()

valid_profile_age_days = float(os.getenv("VALID_PROFILE_AGE_DAYS", 7.0))
expired_cleaner_sleep_minutes = float(os.getenv("EXPIRED_CLEANER_SLEEP_MINUTES", 20.0))
tracker_topic = os.getenv("TRACKER_TOPIC", "platform.payload-status")
listener_metrics_port = os.getenv("LISTENER_METRICS_PORT", 5000)
