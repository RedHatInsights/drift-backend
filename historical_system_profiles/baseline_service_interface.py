from urllib.parse import urljoin

from flask import current_app, request
from kerlescan import config
from kerlescan.constants import (
    AUTH_HEADER_NAME,
    BASELINE_SVC_ENDPOINT,
    INTERNAL_BASELINE_SVC_ENDPOINT,
)
from kerlescan.service_interface import fetch_data, fetch_url, internal_auth_header

from historical_system_profiles import metrics


def fetch_baselines(baseline_ids, service_auth_key, logger):
    """
    fetch baselines
    """

    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    baseline_location = urljoin(config.baseline_svc_hostname, BASELINE_SVC_ENDPOINT)

    message = "reading baselines"
    current_app.logger.audit(message, request=request)
    baseline_result = fetch_data(
        baseline_location,
        auth_header,
        baseline_ids,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )

    return baseline_result


def fetch_system_baseline_associations(system_id, service_auth_key, logger):
    """
    call baseline systems association endpoint to get a list of baselines
    this system is associated with
    """

    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    url = urljoin(config.baseline_svc_hostname, INTERNAL_BASELINE_SVC_ENDPOINT) % system_id

    result = fetch_url(
        url,
        auth_header,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )
    return result
