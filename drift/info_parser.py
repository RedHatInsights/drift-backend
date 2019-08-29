from flask import current_app

from kerlescan.constants import SYSTEM_ID_KEY, COMPARISON_SAME
from kerlescan.constants import COMPARISON_DIFFERENT, COMPARISON_INCOMPLETE_DATA

from kerlescan import profile_parser


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
        system_name = profile_parser.get_name(system_with_profile)
        parsed_system_profile = profile_parser.parse_profile(
            system_with_profile["system_profile"], system_name, current_app.logger
        )
        parsed_system_profiles.append(parsed_system_profile)

    # add baselines into parsed_system_profiles
    for baseline in baselines:
        baseline_facts = {"id": baseline["id"], "name": baseline["display_name"]}
        for baseline_fact in baseline["baseline_facts"]:
            if "value" in baseline_fact:
                baseline_facts[baseline_fact["name"]] = baseline_fact["value"]
            elif "values" in baseline_fact:
                prefix = baseline_fact["name"]
                for nested_fact in baseline_fact["values"]:
                    baseline_facts[prefix + "." + nested_fact["name"]] = nested_fact[
                        "value"
                    ]
        parsed_system_profiles.append(baseline_facts)

    # find the set of all keys to iterate over
    all_keys = set()
    for parsed_system_profile in parsed_system_profiles:
        all_keys = all_keys.union(set(parsed_system_profile.keys()))

    info_comparisons = [
        _create_comparison(parsed_system_profiles, key) for key in all_keys
    ]
    return info_comparisons


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
            "value": system.get(info_name, "N/A") or "N/A",
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
        "display_name": profile_parser.get_name(system),
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
