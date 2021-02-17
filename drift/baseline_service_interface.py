from urllib.parse import urljoin

from drift import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_data
from kerlescan.constants import AUTH_HEADER_NAME, BASELINE_SVC_ENDPOINT


def fetch_baselines(baseline_ids, service_auth_key, logger):
    """
    fetch baselines
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    baseline_location = urljoin(config.baseline_svc_hostname, BASELINE_SVC_ENDPOINT)

    # TODO: (audit-log) read kerlescan/service_interface.py#fetch_data
    baseline_result = fetch_data(
        baseline_location,
        auth_header,
        baseline_ids,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )

    return baseline_result
