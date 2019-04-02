import re

from flask import current_app

from drift.constants import SYSTEM_ID_KEY, COMPARISON_SAME
from drift.constants import COMPARISON_DIFFERENT, COMPARISON_INCOMPLETE_DATA
from drift.constants import SYSTEM_PROFILE_STRINGS, SYSTEM_PROFILE_INTEGERS
from drift.constants import SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED
from drift.constants import SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED

from drift.exceptions import UnparsableNEVRAError


def build_comparisons(systems_with_profiles):
    """
    given a list of system profile dicts and fact namespace, return a dict of
    comparisons, along with a dict of system data
    """
    fact_comparison = _select_applicable_info(systems_with_profiles)

    system_mappings = [_system_mapping(system_with_profile)
                       for system_with_profile in systems_with_profiles]

    sorted_comparison = sorted(fact_comparison, key=lambda comparison: comparison['name'])
    return {'facts': sorted_comparison, 'systems': system_mappings}


def _select_applicable_info(systems_with_profiles):
    """
    Take a list of systems with profiles, and output a "pivoted" list of
    profile facts, where each fact key has a dict of systems and their values. This is
    useful when comparing facts across systems.
    """
    # create dicts of id + info
    parsed_system_profiles = [_parse_profile(system_with_profile['system_profile'])
                              for system_with_profile in systems_with_profiles]

    # find the set of all keys to iterate over
    all_keys = set()
    for parsed_system_profile in parsed_system_profiles:
        all_keys = all_keys.union(set(parsed_system_profile.keys()))

    info_comparisons = [_create_comparison(parsed_system_profiles, key) for key in all_keys]
    return info_comparisons


def _parse_profile(system_profile):
    """
    break complex data structures into more simple structures that can be compared easily.
    """
    # start with metadata that we have brought down from the system record
    parsed_profile = {'id': system_profile[SYSTEM_ID_KEY]}
    # add all strings as-is
    parsed_profile.update({key: system_profile.get(key, None) for key in SYSTEM_PROFILE_STRINGS})

    # add all integers, converting to str
    parsed_profile.update({key: str(system_profile.get(key, None))
                           for key in SYSTEM_PROFILE_INTEGERS})

    # TODO refactor this into a method
    for list_of_strings in SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED:
        for item in system_profile.get(list_of_strings, []):
            parsed_profile.update({list_of_strings + '.' + item: 'enabled'})

    for list_of_strings in SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED:
        parsed_profile.pop(list_of_strings, None)

    for list_of_strings in SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED:
        for item in system_profile.get(list_of_strings, []):
            parsed_profile.update({list_of_strings + '.' + item: 'installed'})

    for list_of_strings in SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED:
        parsed_profile.pop(list_of_strings, None)

    for package in system_profile.get('installed_packages', []):
        try:
            name, epoch, version, release, arch = _get_nevra_from_string(package)
            parsed_profile.update({'installed_packages.' + name: version+'-'+release+'.'+arch})
        except UnparsableNEVRAError as e:
            current_app.logger.warn(e.message)

    parsed_profile.pop('installed_packages', None)

    return parsed_profile


def _get_nevra_from_string(rpm_string):
    """
    this function is originally from vmaas project
    """
    nevra_re = re.compile(r'(([0-9]+):)?(.*)-([^-]+)-([^-]+)\.([a-z0-9_]+)')
    match = nevra_re.match(rpm_string)

    if not match:
        raise UnparsableNEVRAError("unable to parse %s into nevra" % rpm_string)

    _, epoch, name, version, release, arch = match.groups()
    if epoch is None:
        epoch = '0'
    return name, epoch, version, release, arch


def _create_comparison(systems, info_name):
    """
    Take an individual fact, search for it across all systems, and create a dict
    of each system's ID and fact value. Additionally, add a "state" field that
    says if all systems have the same values or different values.

    Note that when passing in "systems" to this method, the ID needs to be listed
    as a fact key.
    """
    info_comparison = COMPARISON_DIFFERENT

    system_id_values = [{'id': system[SYSTEM_ID_KEY],
                         'value': system.get(info_name, "FACT_NOT_SET")}
                        for system in systems]

    system_values = {system['value'] for system in system_id_values}

    if "FACT_NOT_SET" in system_values:
        info_comparison = COMPARISON_INCOMPLETE_DATA
    elif len(system_values) == 1:
        info_comparison = COMPARISON_SAME

    return {'name': info_name, 'state': info_comparison, 'systems': system_id_values}


def _system_mapping(system):
    """
    create a header mapping for one system
    """
    return {'id': system[SYSTEM_ID_KEY], 'fqdn': system['fqdn'], 'last_updated': system['updated']}
