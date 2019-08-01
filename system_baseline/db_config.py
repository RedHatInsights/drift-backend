import os

# please ensure these are all documented in README.md

_db_user = os.getenv("BASELINE_DB_USER", "insights")
_db_password = os.getenv("BASELINE_DB_PASS", "insights")
_db_host = os.getenv("BASELINE_DB_HOST", "localhost")
_db_name = os.getenv("BASELINE_DB_NAME", "insights")

db_uri = f"postgresql://{_db_user}:{_db_password}@{_db_host}/{_db_name}"
db_pool_timeout = int(os.getenv("BASELINE_DB_POOL_TIMEOUT", "5"))
db_pool_size = int(os.getenv("BASELINE_DB_POOL_SIZE", "5"))
