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
    with metrics.inventory_service_requests.time():
        response = requests.get(url, headers=auth_header)
    logger.debug("fetched %s" % url)
    _validate_inventory_response(response, logger)
    return response.json()


def _fetch_data(url, auth_header, system_ids, logger):
    """
    fetch system IDs in batches of 40 for given RESTful URL

    A batch size of 40 was chosen to fetch as many systems per request as we
    can, but still keep some headroom in the URL length.
    """
    BATCH_SIZE = 40
    results = []
    system_ids_to_fetch = system_ids

    while len(system_ids_to_fetch) > 0:
        id_batch = system_ids_to_fetch[:BATCH_SIZE]
        response_json = _fetch_url(url % (','.join(id_batch)), auth_header, logger)
        results += response_json['results']
        system_ids_to_fetch = system_ids_to_fetch[BATCH_SIZE:]

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

    systems_result = _fetch_data(system_location, auth_header, system_ids, logger)
    system_profiles_result = _fetch_data(system_profile_location, auth_header,
                                         system_ids, logger)

    _ensure_correct_system_count(system_ids, systems_result)

    # create a blank profile for each system
    system_profiles = {system['id']: {'system_profile': {}} for system in systems_result}
    # update with actual profile info if we have it
    for profile in system_profiles_result:
        system_profiles[profile['id']] = profile

    systems_without_profile_count = 0
    # fill in any fields that were not on the profile
    for system_id in system_profiles:
        # before we populate the fields, mark where the system profile came
        # from. This is useful so we know if the system has uploaded a tarball
        # or not.
        if system_profiles[system_id]['system_profile']:
            system_profiles[system_id]['system_profile']['system_profile_exists'] = True
        else:
            system_profiles[system_id]['system_profile']['system_profile_exists'] = False
            systems_without_profile_count += 1
        # TODO: populate more than just integers and strings
        for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_STRINGS:
            if key not in system_profiles[system_id]['system_profile']:
                system_profiles[system_id]['system_profile'][key] = 'N/A'

    # record how many no-profile systems were in this report
    metrics.systems_compared_no_sysprofile.observe(systems_without_profile_count)

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
