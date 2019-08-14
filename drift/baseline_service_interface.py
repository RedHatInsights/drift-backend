from urllib.parse import urljoin

from drift import config, metrics
from drift.service_interface import fetch_data, ensure_correct_count
from drift.constants import AUTH_HEADER_NAME, BASELINE_SVC_ENDPOINT


def fetch_baselines(baseline_ids, service_auth_key, logger):
    """
    fetch baselines
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    baseline_location = urljoin(config.baseline_svc_hostname, BASELINE_SVC_ENDPOINT)

    baseline_result = fetch_data(
        baseline_location,
        auth_header,
        baseline_ids,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )
    ensure_correct_count(baseline_ids, baseline_result)

    return baseline_result
