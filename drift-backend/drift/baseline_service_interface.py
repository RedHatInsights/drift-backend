from urllib.parse import urljoin

from flask import current_app, request
from kerlescan import config
from kerlescan.constants import (
    AUTH_HEADER_NAME,
    BASELINE_SVC_ENDPOINT,
    SYSTEM_BASELINE_ADMIN_ENDPOINT,
)
from kerlescan.service_interface import fetch_data, fetch_url, internal_auth_header

from drift import metrics


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


def call_baseline_admin_svc(endpoint, service_auth_key, logger):
    """
    call system-baseline-backend api
    """
    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}}
    baseline_location = urljoin(config.baseline_svc_hostname, SYSTEM_BASELINE_ADMIN_ENDPOINT)

    current_app.logger.audit(
        "calling system-baseline endpoint {}".format(endpoint), request=request
    )

    baseline_result = fetch_url(
        url=baseline_location % endpoint,
        auth_header=auth_header,
        logger=logger,
        time_metric=metrics.baseline_service_requests,
        exception_metric=metrics.baseline_service_exceptions,
    )

    return baseline_result
