from urllib.parse import urljoin

from kerlescan import config
from kerlescan.constants import AUTH_HEADER_NAME, RBAC_SVC_ENDPOINT
from kerlescan.service_interface import fetch_url


def get_perms(application, service_auth_key, logger, request_metric, exception_metric):
    """
    check if user has a permission
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    rbac_location = urljoin(config.rbac_svc_hostname, RBAC_SVC_ENDPOINT) % application
    logger.audit("Fetching RBAC on %s", rbac_location)
    rbac_result = fetch_url(rbac_location, auth_header, logger, request_metric, exception_metric)
    perms = [perm["permission"] for perm in rbac_result["data"]]

    return perms
