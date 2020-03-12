from urllib.parse import urljoin

from drift import metrics
from kerlescan import config
from kerlescan.service_interface import fetch_data
from kerlescan.constants import AUTH_HEADER_NAME, HSP_SVC_ENDPOINT


def fetch_historical_sys_profiles(historical_sys_profile_ids, service_auth_key, logger):
    """
    fetch historical system profiles
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    historical_sys_profile_location = urljoin(config.hsp_svc_hostname, HSP_SVC_ENDPOINT)

    historical_sys_profile_result = fetch_data(
        historical_sys_profile_location,
        auth_header,
        historical_sys_profile_ids,
        logger,
        metrics.historical_sys_profile_service_requests,
        metrics.historical_sys_profile_service_exceptions,
    )

    return historical_sys_profile_result
