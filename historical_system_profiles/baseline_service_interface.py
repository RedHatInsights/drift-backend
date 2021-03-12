from urllib.parse import urljoin

from historical_system_profiles import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_data
from kerlescan.constants import AUTH_HEADER_NAME, INTERNAL_BASELINE_SVC_ENDPOINT


def fetch_system_baseline_associations(system_id, service_auth_key, logger):
    """
    call baseline systems association endpoint to get a list of baselines
    this system is associated with
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    internal_baselines_location = urljoin(
        config.baseline_svc_hostname, INTERNAL_BASELINE_SVC_ENDPOINT
    )

    return fetch_data(
        internal_baselines_location,
        auth_header,
        system_id,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )
