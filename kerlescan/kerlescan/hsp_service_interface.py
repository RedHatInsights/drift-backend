from urllib.parse import urljoin

from kerlescan import config
from kerlescan.constants import AUTH_HEADER_NAME, HSP_SVC_ENDPOINT
from kerlescan.inventory_service_interface import ensure_correct_system_count
from kerlescan.service_interface import fetch_data


def fetch_historical_sys_profiles(historical_sys_profile_ids, service_auth_key, logger, counters):
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
        counters["hsp_service_requests"],
        counters["hsp_service_exceptions"],
    )

    ensure_correct_system_count(historical_sys_profile_ids, historical_sys_profile_result)

    return historical_sys_profile_result
