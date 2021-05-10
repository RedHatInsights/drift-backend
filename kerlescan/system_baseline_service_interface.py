from urllib.parse import urljoin

from kerlescan import config
from kerlescan.service_interface import fetch_url
from kerlescan.constants import (
    AUTH_HEADER_NAME,
    INTERNAL_BASELINE_SVC_DELETE_SYSTEM_ENDPOINT,
)


def delete_systems_from_notifications(system_ids, service_auth_key, logger, counters):
    """
    deletes systems from associations for notifications at system baseline service
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    deletion_request_location = urljoin(
        config.baseline_svc_hostname, INTERNAL_BASELINE_SVC_DELETE_SYSTEM_ENDPOINT
    )

    deletion_request_result = fetch_url(
        deletion_request_location,
        auth_header,
        logger,
        counters["drift_baseline_service_requests"],
        counters["drift_baseline_service_exceptions"],
        "post",
    )

    return deletion_request_result
