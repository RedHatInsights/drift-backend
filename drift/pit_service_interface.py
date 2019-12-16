from urllib.parse import urljoin

from drift import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_data
from kerlescan.constants import AUTH_HEADER_NAME, PIT_SVC_ENDPOINT


def fetch_pits(pit_ids, service_auth_key, logger):
    """
    fetch pits
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    pit_location = urljoin(config.pit_svc_hostname, PIT_SVC_ENDPOINT)

    pit_result = fetch_data(
        pit_location,
        auth_header,
        pit_ids,
        logger,
        metrics.pit_service_requests,
        metrics.pit_service_exceptions,
    )

    return pit_result
