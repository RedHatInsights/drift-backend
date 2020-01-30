from urllib.parse import urljoin

from kerlescan import config
from kerlescan.service_interface import fetch_url
from kerlescan.constants import AUTH_HEADER_NAME, RBAC_SVC_ENDPOINT


def get_roles(application, service_auth_key, logger, request_metric, exception_metric):
    """
    check if user has a role
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    rbac_location = urljoin(config.rbac_svc_hostname, RBAC_SVC_ENDPOINT) % application

    rbac_result = fetch_url(
        rbac_location, auth_header, logger, request_metric, exception_metric
    )
    roles = [role["permission"] for role in rbac_result["data"]]

    return roles
