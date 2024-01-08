from urllib.parse import urljoin

from kerlescan import config
from kerlescan.constants import (
    AUTH_HEADER_NAME,
    INTERNAL_BASELINE_SVC_DELETE_SYSTEM_ENDPOINT,
    INTERNAL_BASELINE_SVC_UPDATE_SYSTEM_ENDPOINT,
)
from kerlescan.service_interface import fetch_url, internal_auth_header


def delete_systems_from_notifications(
    system_ids, service_auth_key, logger, time_metric, exception_metric
):
    """
    deletes systems from associations for notifications at system baseline service
    """

    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    deletion_request_location = urljoin(
        config.baseline_svc_hostname,
        INTERNAL_BASELINE_SVC_DELETE_SYSTEM_ENDPOINT
        % ",".join([str(system_id) for system_id in system_ids]),
    )

    deletion_request_result = fetch_url(
        deletion_request_location,
        auth_header,
        logger,
        time_metric,
        exception_metric,
        "post",
    )

    return deletion_request_result


def update_mapped_system_groups(
    system_id, groups, service_auth_key, logger, time_metric, exception_metric
):
    auth_header = {**{AUTH_HEADER_NAME: service_auth_key}, **internal_auth_header()}

    update_request_url = urljoin(
        config.baseline_svc_hostname, INTERNAL_BASELINE_SVC_UPDATE_SYSTEM_ENDPOINT % str(system_id)
    )

    update_request_result = fetch_url(
        update_request_url,
        auth_header,
        logger,
        time_metric,
        exception_metric,
        "patch",
        json={"groups": groups},
    )

    return update_request_result
