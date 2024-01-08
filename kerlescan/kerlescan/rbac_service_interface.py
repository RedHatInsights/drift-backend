from urllib.parse import urljoin

from kerlescan import config
from kerlescan.constants import AUTH_HEADER_NAME, RBAC_SVC_ENDPOINT
from kerlescan.service_interface import fetch_url


def get_perms(
    application, service_auth_key, logger, request_metric, exception_metric, rbac_filters=None
):
    """
    check if user has a permission
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    rbac_location = urljoin(config.rbac_svc_hostname, RBAC_SVC_ENDPOINT) % application
    logger.audit("Fetching RBAC on %s", rbac_location)
    rbac_data = fetch_url(rbac_location, auth_header, logger, request_metric, exception_metric)[
        "data"
    ]
    perms = [perm["permission"] for perm in rbac_data]

    if rbac_filters is not None and isinstance(rbac_filters, dict):
        # get, parse, merge and store RBAC group filters here
        rbac_filters.update(get_rbac_filters(rbac_data))

    return perms


def get_rbac_filters(rbac_data):
    """Gets RBAC filters from RBAC data"""
    # possible values in "groups.id" key:
    # None - no filter applied, all hosts allowed
    # [] - no groups ids present, no hosts allowed
    # [id1, id2, None] - group ids present, only hosts with id1, id2 or no group (None) allowed

    # select permisions
    permission_list = [
        "inventory:hosts:read",
        "inventory:hosts:*",
        "inventory:*:read",
        "inventory:*:*",
    ]

    # default result is to allow no hosts
    group_ids = []

    def get_attfibute_filter_value(filter):
        value = filter.get("value", None)
        if value is None:
            return value
        elif isinstance(value, list):
            return value
        elif isinstance(value, str):
            # split by comma, parses "null" as None
            return [None if val == "null" else val for val in value.split(",")]
        else:
            raise TypeError

    # get only relevant permission records
    definitions = [
        perm.get("resourceDefinitions", [])
        for perm in rbac_data
        if perm["permission"] in permission_list
    ]

    # if definition contains []
    # then we have empty resource definition for allowed permission thus we allow all hosts
    if [] in definitions:
        group_ids = None

    # flatten definitions so we can work with all of them at once
    definitions = [item for row in definitions for item in row]

    if group_ids is not None:
        # no definition means no matched permission
        if definitions == []:
            group_ids = []
        else:
            # get attributeFilters relevant for inventory groups
            attribute_filters = [
                definition.get("attributeFilter", {})
                for definition in definitions
                if definition.get("attributeFilter", {}).get("key") == "group.id"
            ]

            if attribute_filters == []:
                group_ids = None
            else:
                group_ids = [
                    get_attfibute_filter_value(attribute_filter)
                    for attribute_filter in attribute_filters
                ]
                if None in group_ids:
                    group_ids = None
                else:
                    # flatten them
                    group_ids = [item for row in group_ids for item in row]

    if group_ids:
        group_ids = [{"id": group_id} for group_id in set(group_ids)]

    result = {"group.id": group_ids}

    return result
