from urllib.parse import urljoin

from historical_system_profiles import listener_metrics as metrics
from kerlescan import config
from kerlescan.service_interface import fetch_url
from kerlescan.constants import AUTH_HEADER_NAME, DRIFT_SVC_ENDPOINT


def check_for_drift(system_id, baseline_id, service_auth_key, logger):
    """
    Call short-circuited comparison to check for any changes from baseline
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    drift_location = urljoin(config.drift_svc_hostname, DRIFT_SVC_ENDPOINT)

    drift_url = str(
        drift_location
        + "?system_ids[]="
        + system_id
        + "&baseline_ids[]="
        + baseline_id
        + "&short_circuit=True"
    )

    return fetch_url(
        drift_url,
        auth_header,
        logger,
        metrics.drift_service_requests,
        metrics.drift_service_exceptions,
    )
