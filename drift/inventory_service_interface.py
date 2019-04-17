import json
import requests

from urllib.parse import urljoin

from drift import config, metrics
from drift.constants import AUTH_HEADER_NAME, INVENTORY_SVC_SYSTEMS_ENDPOINT
from drift.constants import INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT, MAX_UUID_COUNT
from drift.constants import SYSTEM_PROFILE_INTEGERS, SYSTEM_PROFILE_STRINGS
from drift.exceptions import SystemNotReturned, InventoryServiceError


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)


def _parse_inventory_response(response, logger):
    """
    return an object based on the inventory response. Raise an expection if the
    response was not what we expected.
    """
    if response.status_code is not requests.codes.ok:
        logger.warn("%s error received from inventory service: %s" %
                    (response.status_code, response.text))
        raise InventoryServiceError("Error received from backend service")

    return json.loads(response.text)


def _ensure_correct_system_count(system_ids_requested, result):
    """
    raise an exception if we didn't get back the number of systems we expected.

    If the count is correct, do nothing.
    """
    if result['count'] < len(system_ids_requested):
        system_ids_returned = {system['id'] for system in result['results']}
        missing_ids = set(system_ids_requested) - system_ids_returned
        raise SystemNotReturned("System(s) %s not available to display" % ','.join(missing_ids))


def fetch_systems_with_profiles(system_ids, service_auth_key, logger):
    """
    fetch systems from inventory service
    """
    if len(system_ids) > MAX_UUID_COUNT:
        raise SystemNotReturned("Too many systems requested, limit is %s" % MAX_UUID_COUNT)

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    system_location = urljoin(config.inventory_svc_hostname,
                              INVENTORY_SVC_SYSTEMS_ENDPOINT)

    system_profile_location = urljoin(config.inventory_svc_hostname,
                                      INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT)

    with metrics.inventory_service_requests.time():
        systems_response = requests.get(system_location % (','.join(system_ids), MAX_UUID_COUNT),
                                        headers=auth_header)
        system_profiles_response = requests.get(system_profile_location % (','.join(system_ids),
                                                                           MAX_UUID_COUNT),
                                                headers=auth_header)

    systems_result = _parse_inventory_response(systems_response, logger)
    system_profiles_result = _parse_inventory_response(system_profiles_response, logger)

    _ensure_correct_system_count(system_ids, systems_result)

    # create a blank profile for each system
    system_profiles = {system['id']: {'system_profile': {}} for system in systems_result['results']}
    # update with actual profile info if we have it
    system_profiles.update({profile['id']: profile
                            for profile in system_profiles_result['results']})

    # fill in any fields that were not on the profile
    for system_id in system_profiles:
        # TODO: populate more than just integers and strings
        for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_STRINGS:
            if key not in system_profiles[system_id]['system_profile']:
                system_profiles[system_id]['system_profile'][key] = 'N/A'

    systems_with_profiles = []
    for system in systems_result['results']:
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
