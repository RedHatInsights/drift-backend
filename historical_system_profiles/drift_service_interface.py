from urllib.parse import urljoin

from historical_system_profiles import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_url, internal_auth_header
from kerlescan.constants import AUTH_HEADER_NAME, DRIFT_SVC_ENDPOINT


def check_for_drift(system_id, baseline_id, service_auth_key, logger):
    """
    Call short-circuited comparison to check for any changes from baseline
    """

    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    drift_location = urljoin(config.drift_svc_hostname, DRIFT_SVC_ENDPOINT)

    drift_url = str(
        drift_location + "?system_ids[]=" + system_id + "&baseline_ids[]=" + baseline_id
    )

    return fetch_url(
        drift_url,
        auth_header,
        logger,
        metrics.drift_service_requests,
        metrics.drift_service_exceptions,
    )
