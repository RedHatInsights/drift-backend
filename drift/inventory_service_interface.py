import requests

from urllib.parse import urljoin

from drift import config, metrics
from drift.constants import AUTH_HEADER_NAME, INVENTORY_SVC_SYSTEMS_ENDPOINT
from drift.constants import INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT
from drift.constants import SYSTEM_PROFILE_INTEGERS, SYSTEM_PROFILE_STRINGS
from drift.exceptions import SystemNotReturned, InventoryServiceError


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)


def _validate_inventory_response(response, logger):
    """
    Raise an exception if the response was not what we expected.
    """
    if response.status_code is not requests.codes.ok:
        logger.warn("%s error received from inventory service: %s" %
                    (response.status_code, response.text))
        raise InventoryServiceError("Error received from backend service")


def _ensure_correct_system_count(system_ids_requested, result):
    """
    raise an exception if we didn't get back the number of systems we expected.

    If the count is correct, do nothing.
    """
    if len(result) < len(system_ids_requested):
        system_ids_returned = {system['id'] for system in result}
        missing_ids = set(system_ids_requested) - system_ids_returned
        raise SystemNotReturned("System(s) %s not available to display" % ','.join(missing_ids))


def _fetch_url(url, auth_header, logger):
    """
    helper to make a single request
    """
    logger.debug("fetching %s" % url)
    response = requests.get(url, headers=auth_header)
    logger.debug("fetched %s" % url)
    _validate_inventory_response(response, logger)
    return response.json()


def _fetch_paginated_url(url, auth_header, logger):
    """
    helper to collate a paginated response
    """
    results = []
    page = 1
    response_json = {'total': 1}

    while len(results) < response_json['total']:
        response_json = _fetch_url(url + ("?page=%s&per_page=20" % page), auth_header, logger)
        results += response_json['results']
        page += 1

    return results


def fetch_systems_with_profiles(system_ids, service_auth_key, logger):
    """
    fetch systems from inventory service
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    system_location = urljoin(config.inventory_svc_hostname,
                              INVENTORY_SVC_SYSTEMS_ENDPOINT)

    system_profile_location = urljoin(config.inventory_svc_hostname,
                                      INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT)

    with metrics.inventory_service_requests.time():
        systems_result = _fetch_paginated_url(system_location % (','.join(system_ids)),
                                              auth_header, logger)
        system_profiles_result = _fetch_paginated_url(system_profile_location %
                                                      (','.join(system_ids)),
                                                      auth_header, logger)

    _ensure_correct_system_count(system_ids, systems_result)

    # create a blank profile for each system
    system_profiles = {system['id']: {'system_profile': {}} for system in systems_result}
    # update with actual profile info if we have it
    system_profiles.update({profile['id']: profile
                            for profile in system_profiles_result})

    # fill in any fields that were not on the profile
    for system_id in system_profiles:
        # before we populate the fields, mark where the system profile came
        # from. This is useful so we know if the system has uploaded a tarball
        # or not.
        if system_profiles[system_id]['system_profile']:
            system_profiles[system_id]['system_profile']['system_profile_exists'] = True
        else:
            system_profiles[system_id]['system_profile']['system_profile_exists'] = False
        # TODO: populate more than just integers and strings
        for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_STRINGS:
            if key not in system_profiles[system_id]['system_profile']:
                system_profiles[system_id]['system_profile'][key] = 'N/A'

    systems_with_profiles = []
    for system in systems_result:
        system_with_profile = system
        # we do not use the 'facts' field
        system_with_profile.pop('facts', None)

        system_with_profile['system_profile'] = system_profiles[system['id']]['system_profile']
        # we duplicate a bit of metadata in the inner dict to make parsing easier
        system_with_profile['system_profile']['id'] = system['id']
        system_with_profile['system_profile']['fqdn'] = system['fqdn']
        system_with_profile['system_profile']['updated'] = system['updated']

        systems_with_profiles.append(system_with_profile)

    return systems_with_profiles
