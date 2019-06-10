import os

# please ensure these are all documented in README.md
log_level = os.getenv("LOG_LEVEL", "INFO")
inventory_svc_hostname = os.getenv(
    "INVENTORY_SVC_URL", "http://inventory_svc_url_is_not_set"
)
prometheus_multiproc_dir = os.getenv("prometheus_multiproc_dir", None)

path_prefix = os.getenv("PATH_PREFIX", "/api/")
app_name = os.getenv("APP_NAME", "drift")
