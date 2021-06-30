import os

from app_common_python import LoadedConfig, isClowderEnabled


def str_to_bool(s):
    try:
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
    except AttributeError:
        raise ValueError("Valid string argument expected")
    raise ValueError("Unable to determine boolean value from given string argument")


def load_hosts_setting(env_name, clowder_endpoint, default):
    if isClowderEnabled():
        cfg = LoadedConfig

        final_endpoint = ""
        for endpoint in cfg.endpoints:
            if endpoint.app == clowder_endpoint:
                final_endpoint = f"http://{endpoint.hostname}:{endpoint.port}"
                return final_endpoint

        if final_endpoint == "":
            return default

    return os.getenv(env_name, default)


inventory_svc_hostname = load_hosts_setting(
    "INVENTORY_SVC_URL", "host-inventory", "http://inventory_svc_url_is_not_set"
)

baseline_svc_hostname = load_hosts_setting(
    "BASELINE_SVC_URL", "system-baseline", "http://baseline_svc_url_is_not_set"
)

rbac_svc_hostname = load_hosts_setting("RBAC_SVC_URL", "rbac", "http://rbac_svc_url_is_not_set")

hsp_svc_hostname = load_hosts_setting("HSP_SVC_URL", "hsp", "http://hsp_svc_url_is_not_set")

drift_svc_hostname = load_hosts_setting("DRIFT_SVC_URL", "drift", "http://drift_svc_url_is_not_set")

log_level = os.getenv("LOG_LEVEL", "INFO")

drift_shared_secret = os.getenv("DRIFT_SHARED_SECRET", None)

prometheus_multiproc_dir = os.getenv("prometheus_multiproc_dir", None)

path_prefix = os.getenv("PATH_PREFIX", "/api/")

enable_rbac = str_to_bool(os.getenv("ENABLE_RBAC", "True"))

enable_smart_mgmt_check = str_to_bool(
    os.getenv("ENABLE_SMART_MANAGEMENT_ENTITLEMENT_CHECK", "False")
)
