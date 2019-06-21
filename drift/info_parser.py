import bitmath
import ipaddress

from flask import current_app
from ipaddress import AddressValueError

from drift.constants import SYSTEM_ID_KEY, COMPARISON_SAME
from drift.constants import COMPARISON_DIFFERENT, COMPARISON_INCOMPLETE_DATA
from drift.constants import SYSTEM_PROFILE_STRINGS, SYSTEM_PROFILE_INTEGERS
from drift.constants import SYSTEM_PROFILE_BOOLEANS
from drift.constants import SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED
from drift.constants import SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED

from drift.exceptions import UnparsableNEVRAError


def build_comparisons(systems_with_profiles, baselines):
    """
    given a list of system profile dicts and fact namespace, return a dict of
    comparisons, along with a dict of system data
    """
    fact_comparisons = _select_applicable_info(systems_with_profiles, baselines)

    system_mappings = [
        _system_mapping(system_with_profile)
        for system_with_profile in systems_with_profiles
    ]

    sorted_system_mappings = sorted(
        system_mappings, key=lambda system: system["display_name"]
    )

    # remove system metadata that we put into to the comparison earlier
    stripped_comparisons = [
        comparison
        for comparison in fact_comparisons
        if comparison["name"] not in {"id", "system_profile_exists"}
    ]

    grouped_comparisons = _group_comparisons(stripped_comparisons)
    sorted_comparisons = sorted(
        grouped_comparisons, key=lambda comparison: comparison["name"]
    )

    baseline_mappings = [_baseline_mapping(baseline) for baseline in baselines]

    return {
        "facts": sorted_comparisons,
        "systems": sorted_system_mappings,
        "baselines": baseline_mappings,
    }


def _group_comparisons(comparisons):
    """
    given a list of comparisons, group similar names. For example:
    [{'name': 'foo.x', ...}, {'name': 'foo.y', ...}, {'name': 'z', ...}]

    becomes:
    [{'name': 'foo', comparisons: [{'name': 'x', ...}, {'name': 'y', ... }], {'name': 'z', ...}]
    """

    def _get_group_name(name):
        n, _, _ = name.partition(".")
        return n

    def _get_value_name(name):
        _, _, n = name.partition(".")
        return n

    def _find_group(name):
        for group in grouped_comparisons:
            if group["name"] == name:
                return group

    # build out group names
    group_names = {_get_group_name(c["name"]) for c in comparisons if "." in c["name"]}
    grouped_comparisons = []
    for group_name in group_names:
        grouped_comparisons.append({"name": group_name, "comparisons": []})

    # populate groups
    for comparison in comparisons:
        if "." in comparison["name"]:
            group = _find_group(_get_group_name(comparison["name"]))
            comparison["name"] = _get_value_name(comparison["name"])
            group["comparisons"].append(comparison)
        else:
            grouped_comparisons.append(comparison)

    # set summary state if grouped comparison contains groups
    for grouped_comparison in grouped_comparisons:
        if "comparisons" in grouped_comparison:
            states = {
                comparison["state"] for comparison in grouped_comparison["comparisons"]
            }
            if COMPARISON_DIFFERENT in states:
                grouped_comparison["state"] = COMPARISON_DIFFERENT
            elif COMPARISON_SAME in states and len(states) == 1:
                grouped_comparison["state"] = COMPARISON_SAME
            else:  # use 'incomplete data' as the fallback state if something goes wrong
                grouped_comparison["state"] = COMPARISON_INCOMPLETE_DATA

    return grouped_comparisons


def _select_applicable_info(systems_with_profiles, baselines):
    """
    Take a list of systems with profiles, and output a "pivoted" list of
    profile facts, where each fact key has a dict of systems and their values. This is
    useful when comparing facts across systems.
    """
    # create dicts of id + info
    parsed_system_profiles = []

    for system_with_profile in systems_with_profiles:
        system_name = _get_name(system_with_profile)
        parsed_system_profile = _parse_profile(
            system_with_profile["system_profile"], system_name
        )
        parsed_system_profiles.append(parsed_system_profile)

    # add baselines into parsed_system_profiles
    for baseline in baselines:
        baseline_facts = {"id": baseline["id"], "name": baseline["display_name"]}
        for baseline_fact in baseline["baseline_facts"]:
            baseline_facts[baseline_fact["name"]] = baseline_fact["value"]
        parsed_system_profiles.append(baseline_facts)

    # find the set of all keys to iterate over
    all_keys = set()
    for parsed_system_profile in parsed_system_profiles:
        all_keys = all_keys.union(set(parsed_system_profile.keys()))

    info_comparisons = [
        _create_comparison(parsed_system_profiles, key) for key in all_keys
    ]
    return info_comparisons


def _parse_profile(system_profile, display_name):
    """
    break complex data structures into more simple structures that can be compared easily.
    display_name is added to data structure for sorting and is later stripped from data structure
    """

    def _parse_lists_of_strings(names, verb):
        """
        helper method to convert lists of strings to comparable facts
        """
        for list_of_strings in names:
            for item in system_profile.get(list_of_strings, []):
                parsed_profile[list_of_strings + "." + item] = verb

    def _parse_running_processes(processes):
        """
        helper method to convert running process lists to facts. We output a
        fact for each process name, with its count as a value. The count is
        returned as a string to match the API spec.
        """
        for process in processes:
            process_fact_name = "running_processes." + process
            if process_fact_name in parsed_profile:
                parsed_profile[process_fact_name] = str(
                    int(parsed_profile[process_fact_name]) + 1
                )
            else:
                parsed_profile[process_fact_name] = "1"

    def _parse_yum_repo(name):
        """
        helper method to convert yum repo objects to comparable facts
        """
        parsed_profile["yum_repos." + name + ".base_url"] = yum_repo.get(
            "base_url", "N/A"
        )
        parsed_profile["yum_repos." + name + ".enabled"] = str(
            yum_repo.get("enabled", "N/A")
        )
        parsed_profile["yum_repos." + name + ".gpgcheck"] = str(
            yum_repo.get("gpgcheck", "N/A")
        )

    def _canonicalize_ipv6_addr(addr):
        """
        helper method to display ipv6 address strings unambiguously. If the address
        is not parsable (for example: 'N/A'), just keep the string as-is.
        """
        try:
            return str(ipaddress.IPv6Address(addr).compressed)
        except AddressValueError:
            return addr

    def _parse_interface(name):
        """
        helper method to convert network interface objects to comparable facts
        """
        ipv6_addresses = [
            _canonicalize_ipv6_addr(addr)
            for addr in interface.get("ipv6_addresses", ["N/A"])
        ]
        parsed_profile["network_interfaces." + name + ".ipv4_addresses"] = ",".join(
            interface.get("ipv4_addresses", ["N/A"])
        )
        parsed_profile["network_interfaces." + name + ".ipv6_addresses"] = ",".join(
            ipv6_addresses
        )
        parsed_profile["network_interfaces." + name + ".mac_address"] = interface.get(
            "mac_address", "N/A"
        )
        parsed_profile["network_interfaces." + name + ".mtu"] = str(
            interface.get("mtu", "N/A")
        )
        parsed_profile["network_interfaces." + name + ".state"] = interface.get(
            "state", "N/A"
        )
        parsed_profile["network_interfaces." + name + ".type"] = interface.get(
            "loopback", "N/A"
        )

    # start with metadata that we have brought down from the system record
    parsed_profile = {"id": system_profile[SYSTEM_ID_KEY], "name": display_name}
    # add all strings as-is
    for key in SYSTEM_PROFILE_STRINGS:
        parsed_profile[key] = system_profile.get(key, None)

    # add all integers, converting to str
    for key in SYSTEM_PROFILE_INTEGERS | SYSTEM_PROFILE_BOOLEANS:
        parsed_profile[key] = str(system_profile.get(key, None))

    _parse_lists_of_strings(SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED, "enabled")
    _parse_lists_of_strings(SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED, "installed")

    _parse_running_processes(system_profile.get("running_processes", []))

    # convert bytes to human readable format
    if "system_memory_bytes" in system_profile:
        with bitmath.format(fmt_str="{value:.2f} {unit}"):
            formatted_size = bitmath.Byte(
                system_profile["system_memory_bytes"]
            ).best_prefix()
            parsed_profile["system_memory"] = str(formatted_size)
        system_profile.pop("system_memory_bytes")

    for package in system_profile.get("installed_packages", []):
        try:
            name, vra = _get_name_vra_from_string(package)
            parsed_profile["installed_packages." + name] = vra
        except UnparsableNEVRAError as e:
            current_app.logger.warn(e.message)

    for interface in system_profile.get("network_interfaces", []):
        try:
            name = interface["name"]
            _parse_interface(name)
        except KeyError:
            current_app.logger.warn("network interface has no name, skipping")
            continue

    for yum_repo in system_profile.get("yum_repos", []):
        try:
            name = yum_repo["name"]
            _parse_yum_repo(name)
        except KeyError:
            current_app.logger.warn("yum repo has no name, skipping")
            continue

    return parsed_profile


def _get_name_vra_from_string(rpm_string):
    """
    small helper to pull name + version/release/arch from string
    """
    split_nevra = rpm_string.split("-")
    if len(split_nevra) < 3:
        raise UnparsableNEVRAError("unable to parse %s into nevra" % rpm_string)
    # grab the version-release.arch
    vra = "-".join(split_nevra[-2:])

    # grab the epoch:name
    epoch_name = "-".join(split_nevra[:-2])
    if ":" in epoch_name:
        # drop the 'epoch:' if it exists
        name = ":".join(epoch_name.split(":")[1:])
    else:
        name = epoch_name

    return name, vra


def _create_comparison(systems, info_name):
    """
    Take an individual fact, search for it across all systems, and create a dict
    of each system's ID and fact value. Additionally, add a "state" field that
    says if all systems have the same values or different values.

    Note that when passing in "systems" to this method, the ID needs to be listed
    as a fact key.
    """
    info_comparison = COMPARISON_DIFFERENT

    system_id_values = [
        {
            "id": system[SYSTEM_ID_KEY],
            "name": system["name"],
            "value": system.get(info_name, "N/A"),
        }
        for system in systems
    ]

    sorted_system_id_values = sorted(
        system_id_values, key=lambda system: system["name"]
    )

    for sorted_system_id_value in sorted_system_id_values:
        del sorted_system_id_value["name"]

    system_values = {system["value"] for system in system_id_values}

    if "N/A" in system_values:
        info_comparison = COMPARISON_INCOMPLETE_DATA
    elif len(system_values) == 1:
        info_comparison = COMPARISON_SAME

    return {
        "name": info_name,
        "state": info_comparison,
        "systems": sorted_system_id_values,
    }


def _system_mapping(system):
    """
    create a header mapping for one system
    """

    system_profile_exists = system["system_profile"]["system_profile_exists"]

    return {
        "id": system[SYSTEM_ID_KEY],
        "display_name": _get_name(system),
        "system_profile_exists": system_profile_exists,
        "last_updated": system.get("updated", None),
    }


def _baseline_mapping(baseline):
    """
    create a header mapping for one baseline
    """

    return {
        "id": baseline["id"],
        "display_name": baseline["display_name"],
        "updated": baseline["updated"],
    }


def _get_name(system):
    # this mimics how the inventory service modal displays names.
    name = system["id"]
    if system.get("fqdn"):
        name = system.get("fqdn")
    if system.get("display_name"):
        name = system.get("display_name")

    return name
