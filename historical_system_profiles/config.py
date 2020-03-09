import os

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
