import logging
import os

from app_common_python import KafkaTopics, LoadedConfig, isClowderEnabled
from kerlescan.config import str_to_bool


def load_db_setting(env_name, attribute, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        return vars(cfg.database)[attribute]

    return os.getenv(env_name, default)


def load_kafka_setting(env_name, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        broker_cfg = cfg.kafka.brokers[0]
        return f"{broker_cfg.hostname}:{broker_cfg.port}"

    return os.getenv(env_name, default).split(",")


def load_kafka_ssl(env_name, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        broker_cfg = cfg.kafka.brokers[0]

        try:
            return broker_cfg.authtype.value == "sasl"
        except AttributeError:
            return False

    return str_to_bool(os.getenv(env_name, default))


def load_kafka_ssl_creds(env_name, attribute, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        broker_cfg = cfg.kafka.brokers[0]

        try:
            if attribute == "username":
                return broker_cfg.sasl.username
            elif attribute == "password":
                return broker_cfg.sasl.password
            elif attribute == "security_protocol":
                return broker_cfg.sasl.securityProtocol
            elif attribute == "sasl_mechanism":
                return broker_cfg.sasl.saslMechanism
        except AttributeError:
            return None

    return os.getenv(env_name, default)


def load_kafka_ssl_cert(env_name, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        broker_cfg = cfg.kafka.brokers[0]
        if broker_cfg.cacert:
            return cfg.kafka_ca()
        else:
            return None

    return os.getenv(env_name, default)


"""def load_kafka_security_protocol(env_name, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        broker_cfg = cfg.kafka.brokers[0]

        try:
            return broker_cfg.authtype
        except AttributeError:
            return None

    return os.getenv(env_name, default)"""


def topic(topic):
    if isClowderEnabled():
        return KafkaTopics[topic].name
    return topic


# pull the app name from the env var; we are not fully initialized yet
app_name = os.getenv("APP_NAME", "historical-system-profiles")
logger = logging.getLogger(app_name)


# please ensure these are all documented in README.md
_db_user = load_db_setting("HSP_DB_USER", "username", "insights")
_db_password = load_db_setting("HSP_DB_PASS", "password", "insights")
_db_host = load_db_setting("HSP_DB_HOST", "hostname", "localhost")
_db_name = load_db_setting("HSP_DB_NAME", "name", "insights")
_db_port = load_db_setting("HSP_DB_PORT", "port", "5432")

db_uri = f"postgresql://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
db_pool_timeout = int(os.getenv("HSP_DB_POOL_TIMEOUT", "5"))
db_pool_size = int(os.getenv("HSP_DB_POOL_SIZE", "5"))

bootstrap_servers = load_kafka_setting("BOOTSTRAP_SERVERS", "kafka:29092")
consume_topic = topic(os.getenv("CONSUME_TOPIC", "platform.inventory.events"))
listener_type = os.getenv("LISTENER_TYPE", "ARCHIVER")
kafka_group_id = os.getenv("KAFKA_GROUP_ID", "hsp-%s" % listener_type.lower())
notification_service_topic = topic(
    os.getenv("NOTIFICATION_SERVICE_TOPIC", "platform.notifications.ingress")
)
notification_bundle = os.getenv("NOTIFICATION_BUNDLE", "rhel")
notification_app = os.getenv("NOTIFICATION_APP", "drift")

enable_kafka_ssl = load_kafka_ssl("ENABLE_KAFKA_SSL", "False")
kafka_ssl_cert = load_kafka_ssl_cert("KAFKA_SSL_CERT", "/opt/certs/kafka-cacert")
kafka_sasl_username = load_kafka_ssl_creds("KAFKA_SASL_USERNAME", "username", None)
kafka_sasl_password = load_kafka_ssl_creds("KAFKA_SASL_PASSWORD", "password", None)
kafka_security_protocol = load_kafka_ssl_creds(
    "KAFKA_SECURITY_PROTOCOL", "security_protocol", "PLAINTEXT"
)
kafka_sasl_mechanism = load_kafka_ssl_creds("KAFKA_SASL_MECHANISM", "sasl_mechanism", "PLAIN")

# logging params used outside of flask
aws_access_key_id = os.getenv("CW_AWS_ACCESS_KEY_ID", None)
aws_secret_access_key = os.getenv("CW_AWS_SECRET_ACCESS_KEY", None)
aws_region_name = os.getenv("CW_AWS_REGION_NAME", "us-east-1")
log_group = os.getenv("CW_LOG_GROUP", "platform-dev")
log_sql_statements = str_to_bool(os.getenv("LOG_SQL_STATEMENTS", "False"))
hostname = os.getenv("HOSTNAME", "hsp-hostname-not-set")

valid_profile_age_days = float(os.getenv("VALID_PROFILE_AGE_DAYS", 7.0))
expired_cleaner_sleep_minutes = float(os.getenv("EXPIRED_CLEANER_SLEEP_MINUTES", 20.0))
tracker_topic = topic(os.getenv("TRACKER_TOPIC", "platform.payload-status"))
listener_metrics_port = int(os.getenv("LISTENER_METRICS_PORT", 5000))
listener_delay = int(os.getenv("LISTENER_DELAY", 5))
kafka_max_poll_interval_ms = int(os.getenv("KAFKA_MAX_POLL_INTERVAL_MS", 300000))
kafka_max_poll_records = int(os.getenv("KAFKA_MAX_POLL_RECORDS", 500))

liveness_probe_filepath = os.path.abspath(os.getenv("LIVENESS_PROBE_FILE", "liveness_probe"))
readiness_probe_filepath = os.path.abspath(os.getenv("READINESS_PROBE_FILE", "readiness_probe"))
