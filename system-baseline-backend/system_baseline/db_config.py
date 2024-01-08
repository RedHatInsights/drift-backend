import os

from app_common_python import LoadedConfig, isClowderEnabled


def load_db_setting(env_name, attribute, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        return vars(cfg.database)[attribute]

    return os.getenv(env_name, default)


# please ensure these are all documented in README.md

_db_user = load_db_setting("BASELINE_DB_USER", "username", "insights")
_db_password = load_db_setting("BASELINE_DB_PASS", "password", "insights")
_db_host = load_db_setting("BASELINE_DB_HOST", "hostname", "localhost")
_db_port = load_db_setting("BASELINE_DB_PORT", "port", "5432")
_db_name = load_db_setting("BASELINE_DB_NAME", "name", "baselinedb")

db_uri = f"postgresql://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
db_pool_timeout = int(os.getenv("BASELINE_DB_POOL_TIMEOUT", "5"))
db_pool_size = int(os.getenv("BASELINE_DB_POOL_SIZE", "5"))
