from urllib.parse import urljoin

from historical_system_profiles import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_url, internal_auth_header
from kerlescan.constants import AUTH_HEADER_NAME, INTERNAL_BASELINE_SVC_ENDPOINT


def fetch_system_baseline_associations(system_id, service_auth_key, logger):
    """
    call baseline systems association endpoint to get a list of baselines
    this system is associated with
    """

    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    internal_baselines_location = urljoin(
        config.baseline_svc_hostname, INTERNAL_BASELINE_SVC_ENDPOINT
    )

    query = "?system_id=%s" % system_id
    url = internal_baselines_location % query
    result =  fetch_url(
        url,
        auth_header,
        logger,
        metrics.baseline_service_requests,
        metrics.baseline_service_exceptions,
    )
    return result
