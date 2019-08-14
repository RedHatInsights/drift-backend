from urllib.parse import urljoin

from drift import config, metrics
from drift.constants import AUTH_HEADER_NAME, INVENTORY_SVC_SYSTEMS_ENDPOINT
from drift.constants import INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT
from drift.constants import SYSTEM_PROFILE_INTEGERS, SYSTEM_PROFILE_STRINGS
from drift.service_interface import fetch_data, ensure_correct_count


def fetch_systems_with_profiles(system_ids, service_auth_key, logger):
    """
    fetch systems from inventory service
    """

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    system_location = urljoin(
        config.inventory_svc_hostname, INVENTORY_SVC_SYSTEMS_ENDPOINT
    )

    system_profile_location = urljoin(
        config.inventory_svc_hostname, INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT
    )

    systems_result = fetch_data(
        system_location,
        auth_header,
        system_ids,
        logger,
        metrics.inventory_service_requests,
        metrics.inventory_service_exceptions,
    )
    system_profiles_result = fetch_data(
        system_profile_location,
        auth_header,
        system_ids,
        logger,
        metrics.inventory_service_requests,
        metrics.inventory_service_exceptions,
    )

    ensure_correct_count(system_ids, systems_result)

    # create a blank profile for each system
    system_profiles = {
        system["id"]: {"system_profile": {}} for system in systems_result
    }
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
            system_profiles[system_id]["system_profile"][
                "system_profile_exists"
            ] = False
            systems_without_profile_count += 1
        # TODO: populate more than just integers and strings
        for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_STRINGS:
            if key not in system_profiles[system_id]["system_profile"]:
                system_profiles[system_id]["system_profile"][key] = "N/A"

    # record how many no-profile systems were in this report
    metrics.systems_compared_no_sysprofile.observe(systems_without_profile_count)

    systems_with_profiles = []
    for system in systems_result:
        system_with_profile = system
        # we do not use the 'facts' field
        system_with_profile.pop("facts", None)

        system_with_profile["system_profile"] = system_profiles[system["id"]][
            "system_profile"
        ]
        # we duplicate a bit of metadata in the inner dict to make parsing easier
        system_with_profile["system_profile"]["id"] = system["id"]
        system_with_profile["system_profile"]["fqdn"] = system["fqdn"]
        system_with_profile["system_profile"]["updated"] = system["updated"]

        systems_with_profiles.append(system_with_profile)

    return systems_with_profiles
