import os


# small helper to convert strings to boolean
def str_to_bool(s):
    try:
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
    except AttributeError:
        raise ValueError("Valid string argument expected")
    raise ValueError("Unable to determine boolean value from given string argument")


log_level = os.getenv("LOG_LEVEL", "INFO")
inventory_svc_hostname = os.getenv(
    "INVENTORY_SVC_URL", "http://inventory_svc_url_is_not_set"
)
baseline_svc_hostname = os.getenv(
    "BASELINE_SVC_URL", "http://baseline_svc_url_is_not_set"
)
rbac_svc_hostname = os.getenv("RBAC_SVC_URL", "http://rbac_svc_url_is_not_set")
hsp_svc_hostname = os.getenv("HSP_SVC_URL", "http://hsp_svc_url_is_not_set")
prometheus_multiproc_dir = os.getenv("prometheus_multiproc_dir", None)

path_prefix = os.getenv("PATH_PREFIX", "/api/")

enable_rbac = str_to_bool(os.getenv("ENABLE_RBAC", "True"))

enable_smart_mgmt_check = str_to_bool(
    os.getenv("ENABLE_SMART_MANAGEMENT_ENTITLEMENT_CHECK", "False")
)
