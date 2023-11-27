import concurrent.futures

from urllib.parse import urljoin

from kerlescan import config
from kerlescan.constants import (
    AUTH_HEADER_NAME,
    FILTERED_OUT_OPERATING_SYSTEMS,
    INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT,
    INVENTORY_SVC_SYSTEM_TAGS_ENDPOINT,
    INVENTORY_SVC_SYSTEMS_ENDPOINT,
    SYSTEM_PROFILE_INTEGERS,
    SYSTEM_PROFILE_STRINGS,
)
from kerlescan.exceptions import ItemNotReturned
from kerlescan.service_interface import fetch_data


def ensure_correct_system_count(system_ids_requested, result):
    """
    raise an exception if we didn't get back the number of systems we expected.

    If the count is correct, do nothing.
    """
    if len(result) < len(system_ids_requested):
        system_ids_returned = {system["id"] for system in result}
        missing_ids = set(system_ids_requested) - system_ids_returned
        raise ItemNotReturned("ids [%s] not available to display" % ", ".join(missing_ids))


def filter_out_systems(systems_with_profiles):
    # remove CentOS Linux systems
    systems_with_profiles = [
        system
        for system in systems_with_profiles
        if system.get("system_profile", {}).get("operating_system", {}).get("name")
        not in FILTERED_OUT_OPERATING_SYSTEMS
    ]

    return systems_with_profiles


def interleave_systems_and_profiles(systems_result, system_profiles_result, system_tags_result):
    """
    given a system result and system profile result, interleave them and create
    records suitable for a drift comparison.
    """
    # create a blank profile for each system
    system_profiles = {system["id"]: {"system_profile": {}} for system in systems_result}
    # update with actual profile info if we have it
    for profile in system_profiles_result:
        system_profiles[profile["id"]] = profile

    systems_without_profile_count = 0
    # fill in any fields that were not on the profile
    for system_id in system_profiles:
        # before we populate the fields, mark where the system profile came
        # from. This is useful so we know if the system has uploaded a tarball
        # or not.
        if system_profiles[system_id]["system_profile"]:
            system_profiles[system_id]["system_profile"]["system_profile_exists"] = True
        else:
            system_profiles[system_id]["system_profile"]["system_profile_exists"] = False
            systems_without_profile_count += 1
        # TODO: populate more than just integers and strings
        for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_STRINGS:
            if key not in system_profiles[system_id]["system_profile"]:
                system_profiles[system_id]["system_profile"][key] = "N/A"

    systems_with_profiles = []
    for system in systems_result:
        system_with_profile = system
        # we do not use the 'facts' field
        system_with_profile.pop("facts", None)

        system_with_profile["system_profile"] = system_profiles[system["id"]]["system_profile"]
        # we duplicate a bit of metadata in the inner dict to make parsing easier
        system_with_profile["system_profile"]["id"] = system["id"]
        system_with_profile["system_profile"]["fqdn"] = system["fqdn"]
        system_with_profile["system_profile"]["updated"] = system["updated"]
        system_with_profile["system_profile"]["stale_warning_timestamp"] = system[
            "stale_warning_timestamp"
        ]

        # now add tags if any exist for the system.
        # system_tags_result is a dict keyed on uuid.
        if system_tags_result.get(system["id"]):
            system_with_profile["system_profile"]["tags"] = system_tags_result[system["id"]]

        systems_with_profiles.append(system_with_profile)

    return systems_with_profiles


def fetch_systems_with_profiles(system_ids, service_auth_key, logger, counters):
    """
    fetch systems from inventory service
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    system_location = urljoin(config.inventory_svc_hostname, INVENTORY_SVC_SYSTEMS_ENDPOINT)

    system_profile_location = urljoin(
        config.inventory_svc_hostname, INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT
    )

    system_tags_location = urljoin(
        config.inventory_svc_hostname, INVENTORY_SVC_SYSTEM_TAGS_ENDPOINT
    )

    futures = {}
    api_results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        systems_result_future = executor.submit(
            fetch_data,
            system_location,
            auth_header,
            system_ids,
            logger,
            counters["inventory_service_requests"],
            counters["inventory_service_exceptions"],
        )
        futures[systems_result_future] = "systems_result"

        system_profiles_future = executor.submit(
            fetch_data,
            system_profile_location,
            auth_header,
            system_ids,
            logger,
            counters["inventory_service_requests"],
            counters["inventory_service_exceptions"],
        )
        futures[system_profiles_future] = "system_profiles_result"

        system_tags_future = executor.submit(
            fetch_data,
            system_tags_location,
            auth_header,
            system_ids,
            logger,
            counters["inventory_service_requests"],
            counters["inventory_service_exceptions"],
        )
        futures[system_tags_future] = "system_tags_result"

        for future in concurrent.futures.as_completed(futures):
            api_results[futures[future]] = future.result()

    systems_result = api_results.get("systems_result", [])
    system_profiles_result = api_results.get("system_profiles_result", [])
    system_tags_result = api_results.get("system_tags_result", [])

    ensure_correct_system_count(system_ids, systems_result)

    systems_with_profiles = interleave_systems_and_profiles(
        systems_result, system_profiles_result, system_tags_result
    )

    return filter_out_systems(systems_with_profiles)
