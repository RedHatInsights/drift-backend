import re

from dateutil.parser import parse as dateparse
from flask import current_app
from kerlescan import profile_parser
from kerlescan.constants import (
    COMPARISON_DIFFERENT,
    COMPARISON_INCOMPLETE_DATA,
    COMPARISON_INCOMPLETE_DATA_OBFUSCATED,
    COMPARISON_SAME,
    OBFUSCATED_FACTS_PATTERNS,
    SAP_RELATED_FACTS,
    SYSTEM_ID_KEY,
)

from drift.metrics import performance_timing


PT_BC_SELECT_APPLICABLE_INFO = performance_timing.labels(
    method="build_comparisons", method_part="select_applicable_info"
)


def build_comparisons(
    systems_with_profiles,
    baselines,
    historical_sys_profiles,
    reference_id,
    short_circuit,
):
    """
    given a list of system profile dicts and fact namespace, return a dict of
    comparisons, along with a dict of system data

    Unless short_circuit is True, then we don't need a full comparison report, only a
    report covering the facts present on the baseline as this is for notifications if
    a newly checked in hsp system has drifted from an associated baseline.
    The key 'drift_event_notify' will be true on the report if the system has drifted
    from the associated baseline, otherwise it will be false.
    """

    with PT_BC_SELECT_APPLICABLE_INFO.time():
        fact_comparisons = _select_applicable_info(
            systems_with_profiles,
            baselines,
            historical_sys_profiles,
            reference_id,
            short_circuit,
        )

    drift_event_notify = False

    # remove system metadata that we put into to the comparison earlier
    stripped_comparisons = []
    metadata_fields = {"name", "id", "system_profile_exists", "is_baseline"}
    for comparison in fact_comparisons:
        if comparison["name"] not in metadata_fields:
            stripped_comparisons.append(comparison)
            # if the system has drifted from the baseline, notify
            if short_circuit:
                if comparison["drifted_from_baseline"]:
                    drift_event_notify = True

    grouped_comparisons = _group_comparisons(stripped_comparisons)
    sorted_comparisons = sorted(grouped_comparisons, key=lambda comparison: comparison["name"])

    # create metadata
    baseline_mappings = [_baseline_mapping(baseline) for baseline in baselines]
    historical_sys_profile_mappings = [
        _historical_sys_profile_mapping(historical_sys_profile)
        for historical_sys_profile in historical_sys_profiles
    ]
    system_mappings = [
        _system_mapping(system_with_profile) for system_with_profile in systems_with_profiles
    ]
    sorted_system_mappings = sorted(system_mappings, key=lambda system: system["display_name"])

    sorted_historical_sys_profile_mappings = sorted(
        historical_sys_profile_mappings,
        key=lambda hsp: dateparse(hsp["updated"]),
        reverse=True,
    )

    return {
        "facts": sorted_comparisons,
        "systems": sorted_system_mappings,
        "baselines": baseline_mappings,
        "historical_system_profiles": sorted_historical_sys_profile_mappings,
        "drift_event_notify": drift_event_notify,
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
            group["comparisons"] = sorted(
                group["comparisons"], key=lambda comparison: comparison["name"]
            )
        else:
            grouped_comparisons.append(comparison)

    # set summary state if grouped comparison contains groups
    for grouped_comparison in grouped_comparisons:
        if "comparisons" in grouped_comparison:
            states = {comparison["state"] for comparison in grouped_comparison["comparisons"]}
            if COMPARISON_DIFFERENT in states:
                grouped_comparison["state"] = COMPARISON_DIFFERENT
            elif COMPARISON_INCOMPLETE_DATA in states:
                if COMPARISON_SAME in states:
                    grouped_comparison["state"] = COMPARISON_DIFFERENT
                else:
                    grouped_comparison["state"] = COMPARISON_INCOMPLETE_DATA
            elif COMPARISON_SAME in states and len(states) == 1:
                grouped_comparison["state"] = COMPARISON_SAME
            else:  # use 'incomplete data' as the fallback state if something goes wrong
                grouped_comparison["state"] = COMPARISON_INCOMPLETE_DATA

    return grouped_comparisons


def _select_applicable_info(
    systems_with_profiles,
    baselines,
    historical_sys_profiles,
    reference_id,
    short_circuit,
):
    """
    Take a list of systems with profiles, and output a "pivoted" list of
    profile facts, where each fact key has a dict of systems and their values. This is
    useful when comparing facts across systems.

    Unless short_circuit is True, then we don't need a full comparison report, only one for
    facts present on a single baseline that is being compared with a single system for
    notifications if a newly checked in hsp system has drifted from an associated baseline.
    If the key 'drifted_from_baseline' is True, the system has drifted, else False.
    """
    # create dicts of id + info
    parsed_system_profiles = []

    for system_with_profile in systems_with_profiles:
        system_name = profile_parser.get_name(system_with_profile)
        parsed_system_profile = profile_parser.parse_profile(
            system_with_profile["system_profile"], system_name, current_app.logger
        )
        parsed_system_profiles.append({**parsed_system_profile, "is_baseline": False})

    for historical_sys_profile in historical_sys_profiles:
        historical_sys_profile_name = historical_sys_profile["display_name"]
        parsed_historical_sys_profile = profile_parser.parse_profile(
            historical_sys_profile["system_profile"],
            historical_sys_profile_name,
            current_app.logger,
        )
        parsed_system_profiles.append({**parsed_historical_sys_profile, "is_baseline": False})

    # add baselines into parsed_system_profiles
    for baseline in baselines:
        baseline_facts = {"id": baseline["id"], "name": baseline["display_name"]}
        for baseline_fact in baseline["baseline_facts"]:
            if "value" in baseline_fact:
                baseline_facts[baseline_fact["name"]] = baseline_fact["value"]
            elif "values" in baseline_fact:
                prefix = baseline_fact["name"]
                for nested_fact in baseline_fact["values"]:
                    baseline_facts[prefix + "." + nested_fact["name"]] = nested_fact["value"]
        parsed_system_profiles.append({**baseline_facts, "is_baseline": True})

    # find the set of all keys to iterate over
    # if short_circuit is True, we only want the facts present in this baseline
    # since we are comparing one baseline to one system for notifications only
    all_keys = set()
    if short_circuit:
        for parsed_system_profile in parsed_system_profiles:
            if parsed_system_profile["is_baseline"]:
                all_keys = set(parsed_system_profile.keys())
    else:
        for parsed_system_profile in parsed_system_profiles:
            all_keys = all_keys.union(set(parsed_system_profile.keys()))

    # prepare regexes for obfuscated values matching
    obfuscated_regexes = {}
    for key in OBFUSCATED_FACTS_PATTERNS.keys():
        obfuscated_regexes[key] = re.compile(OBFUSCATED_FACTS_PATTERNS[key])

    info_comparisons = []
    for key in all_keys:

        # obfuscated information type - key
        for obfuscated_key in obfuscated_regexes.keys():
            if obfuscated_key in key:
                for system in parsed_system_profiles:
                    system["obfuscation"] = {}
                    system["obfuscation"][key] = False
                    obfuscated_regex = obfuscated_regexes[obfuscated_key]
                    value = system.get(key)
                    # only if value is present and matches with obfuscated pattern
                    if value and obfuscated_regex.match(value):
                        system["obfuscation"][key] = True

        current_comparison = _create_comparison(
            parsed_system_profiles,
            key,
            reference_id,
            len(systems_with_profiles),
            short_circuit,
        )
        if current_comparison:
            # if short_circuit is True, and there was a change, i.e. this system
            # has drifted from this associated baseline, then set the key on the
            # comparison 'drifted_from_baseline' to True to trigger a notification
            # else set it to False.
            if short_circuit and current_comparison["state"] == COMPARISON_DIFFERENT:
                current_comparison["drifted_from_baseline"] = True
            else:
                current_comparison["drifted_from_baseline"] = False
            info_comparisons.append(current_comparison)
    return info_comparisons


def _create_comparison(systems, info_name, reference_id, system_count, short_circuit):
    """
    Take an individual fact, search for it across all systems, and create a dict
    of each system's ID and fact value. Additionally, add a "state" field that
    says if all systems have the same values or different values.

    Note that when passing in "systems" to this method, the ID needs to be listed
    as a fact key.

    Also the system_count is the count of "actual" systems. If we are comparing
    multiple systems to each other, we use different rules for items that
    should be unique across systems like IP address.

    If short_circuit is True, we are only interested in whether the children of a
    multivalue fact's state when those child-facts are present on the baseline
    and not the state of the overall parent.  This is because short_circuit is
    used when we wish to trigger a notification for drift of a newly checked in
    system from an associated baseline and we are then only interested in the facts
    present on that associated baseline.

    """
    # TODO: this method is messy and could be refactored
    if info_name in SAP_RELATED_FACTS:
        sap_present = False
        for system in systems:
            if "sap_system" in system and str(system["sap_system"]) == "True":
                sap_present = True
        if not sap_present:
            return

    info_comparison = COMPARISON_DIFFERENT

    system_id_values = [
        {
            "id": system[SYSTEM_ID_KEY],
            "name": system["name"],
            "value": system.get(info_name, "N/A") or "N/A",
            "is_obfuscated": system.get("obfuscation", {}).get(info_name, False),
            "is_baseline": system["is_baseline"],
        }
        for system in systems
    ]

    sorted_system_id_values = sorted(system_id_values, key=lambda system: system["name"])

    sorted_system_id_values = sorted(
        sorted_system_id_values, key=lambda system: system["is_baseline"], reverse=True
    )

    multivalue = False
    for value in sorted_system_id_values:
        if isinstance(value.get("value", "N/A"), list):
            multivalue = True

    # standard logic for single value facts
    # NOTE: This will need to be changed when obfuscated values can also be
    # in multi-value facts
    if not multivalue:
        sorted_system_id_values_without_obfuscated = [
            system for system in sorted_system_id_values if not system.get("is_obfuscated")
        ]

        system_values = {system["value"] for system in sorted_system_id_values_without_obfuscated}

        if "N/A" in system_values:  # one or more values are missing
            info_comparison = COMPARISON_DIFFERENT
        elif len(system_values) <= 1:  # when there is only one or zero non-obfuscated values left
            info_comparison = COMPARISON_SAME

        # we specifically want to check for more than one system not baselines below
        # so build the baseline count here
        baseline_count = 0
        for system_id_value in sorted_system_id_values_without_obfuscated:
            if system_id_value["is_baseline"]:
                baseline_count += 1

        # override comparison logic for certain fact names
        # use the baseline count above to check for more than one system specifically
        if _is_unique_rec_name(info_name) and (system_count - baseline_count) > 1:
            system_values_with_duplicates = [
                system["value"] for system in sorted_system_id_values_without_obfuscated
            ]
            # we want to show status as incomplete for "N/A" values now
            if "N/A" in system_values:
                info_comparison = COMPARISON_INCOMPLETE_DATA
            elif len(system_values) == len(system_values_with_duplicates):
                info_comparison = COMPARISON_SAME
            else:
                info_comparison = COMPARISON_DIFFERENT

        if _is_no_rec_name(info_name):
            info_comparison = COMPARISON_SAME

        # change "N/A" to empty string for better display, and remove
        # fields we added to assist with sorting
        for system_id_value in sorted_system_id_values:
            if system_id_value["value"] == "N/A":
                system_id_value["value"] = ""

            del system_id_value["name"]
            del system_id_value["is_baseline"]
            if not system_id_value["is_obfuscated"]:
                del system_id_value["is_obfuscated"]

        if reference_id and info_comparison != COMPARISON_SAME:
            # pull the reference_value for this comparison
            reference_value = None
            for values in sorted_system_id_values_without_obfuscated:
                if values["id"] == reference_id:
                    reference_value = values["value"]

            for values in sorted_system_id_values_without_obfuscated:
                values["state"] = COMPARISON_SAME
                if values["value"] != reference_value:
                    values["state"] = COMPARISON_DIFFERENT

        if len(system_values) == 1:
            info_comparison = COMPARISON_SAME

        if (
            len(sorted_system_id_values) - len(sorted_system_id_values_without_obfuscated) > 0
        ):  # when there is one or more obfuscated values
            info_comparison = COMPARISON_INCOMPLETE_DATA_OBFUSCATED

        return {
            "name": info_name,
            "state": info_comparison,
            "systems": sorted_system_id_values,
        }

    else:
        # multivalue fact handling
        all_value_options = set()
        sorted_system_values = []
        if reference_id:
            for system in sorted_system_id_values:
                sorted_system_values.append(system["value"])
                if reference_id == system["id"]:
                    reference_value = system["value"]
        else:
            sorted_system_values = [system["value"] for system in sorted_system_id_values]

        for value in sorted_system_values:
            if not isinstance(value, list):
                if value != "N/A":
                    all_value_options.add(value)
            else:
                for item in value:
                    all_value_options.add(item)

        row_count = len(all_value_options)
        sorted_all_value_options = sorted(list(all_value_options))
        value_count = 0
        multivalue_comparisons = [COMPARISON_SAME] * row_count
        info_comparison = COMPARISON_SAME
        for value in sorted_system_values:
            row = 0
            column = []
            if not isinstance(value, list):
                while row < row_count:
                    if sorted_all_value_options[row] == value:
                        column.append(value)
                    else:
                        column.append("")
                        info_comparison = COMPARISON_DIFFERENT
                        multivalue_comparisons[row] = COMPARISON_DIFFERENT
                    row += 1
            else:
                while row < row_count:
                    if sorted_all_value_options[row] in value:
                        column.append(sorted_all_value_options[row])
                    else:
                        column.append("")
                        info_comparison = COMPARISON_DIFFERENT
                        multivalue_comparisons[row] = COMPARISON_DIFFERENT
                    row += 1
            sorted_system_id_values[value_count]["value"] = column
            value_count += 1

        # If short_circuit is true, this is a comparison of one system that just
        # checked in to an associated baseline, and we only want to notify of
        # drift if the facts present on that baseline are different on the system.
        # The baseliine is sorted first, so check each fact in the first column
        # to see if that fact is in the second column (the system) and adjust
        # the info_comparison value accordingly.
        if short_circuit:
            info_comparison = COMPARISON_SAME
            for value in sorted_system_id_values[0]["value"]:
                if value != "":
                    if value not in sorted_system_id_values[1]["value"]:
                        info_comparison = COMPARISON_DIFFERENT

        row = 0
        multivalues = []
        while row < row_count:
            expanded_systems = []
            state = info_comparison
            reference = next(
                filter(lambda v: v["id"] == reference_id, sorted_system_id_values), None
            )
            for system in sorted_system_id_values:
                if reference_id:
                    reference_value = reference["value"][row]
                    if not isinstance(system["value"], list):
                        if system["value"] == reference_value:
                            state = COMPARISON_SAME
                        else:
                            state = COMPARISON_DIFFERENT
                    else:
                        if system["value"][row] == reference_value:
                            state = COMPARISON_SAME
                        else:
                            state = COMPARISON_DIFFERENT
                expanded_systems.append(
                    {"id": system["id"], "value": system["value"][row], "state": state}
                )
            multivalues.append({"state": multivalue_comparisons[row], "systems": expanded_systems})
            row += 1

        # change "N/A" to empty string for better display, and remove
        # fields we added to assist with sorting
        for system_id_value in sorted_system_id_values:
            if system_id_value["value"] == "N/A":
                system_id_value["value"] = ""

            del system_id_value["name"]
            del system_id_value["is_baseline"]
            # remove is_obfuscaed if it's None or False
            # currently always the case for multivalue
            del system_id_value["is_obfuscated"]

        return {
            "name": info_name,
            "state": info_comparison,
            "multivalues": multivalues,
            "systems": sorted_system_id_values,
        }


def _is_unique_rec_name(info_name):
    """
    helper method to see if we should use the uniqueness recommendation on the
    fact comparison
    """
    UNIQUE_INFO_SUFFIXES = [".ipv4_addresses", ".ipv6_addresses", ".mac_address"]
    UNIQUE_INFO_PREFIXES = ["fqdn"]

    if info_name.startswith("network_interfaces.lo."):
        return False

    for prefix in UNIQUE_INFO_PREFIXES:
        if info_name.startswith(prefix):
            return True

    for suffix in UNIQUE_INFO_SUFFIXES:
        if info_name.endswith(suffix):
            return True

    return False


def _is_no_rec_name(info_name):
    """
    helper method to see if we should not provide any recommendation
    """
    if info_name == "last_boot_time":
        return True


def _system_mapping(system):
    """
    create a header mapping for one system
    """
    system_profile_exists = system["system_profile"]["system_profile_exists"]
    captured_or_updated = system.get("updated", None)
    if system_profile_exists:
        if "captured_date" in system["system_profile"]:
            captured_or_updated = system["system_profile"]["captured_date"]
    return {
        "id": system[SYSTEM_ID_KEY],
        "display_name": profile_parser.get_name(system),
        "system_profile_exists": system_profile_exists,
        "last_updated": captured_or_updated,
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


def _historical_sys_profile_mapping(historical_sys_profile):
    """
    create a header mapping for one historical profile

    note that we use "captured_date" for the "updated" field, to retain API
    compatability. Users are typically interested in the captured_date here and
    not the internal updated timestamp.
    """
    return {
        "id": historical_sys_profile["id"],
        "display_name": historical_sys_profile["display_name"],
        "updated": historical_sys_profile["captured_date"],
        "system_id": historical_sys_profile["inventory_id"],
    }
