from pandas.io.json import json_normalize

from drift.constants import SYSTEM_ID_KEY, COMPARISON_SAME
from drift.constants import COMPARISON_DIFFERENT, COMPARISON_INCOMPLETE_DATA


def build_comparisons(inventory_service_systems, fact_namespace):
    """
    given a list of system dicts and fact namespace, return a dict of comparisons, along with a
    dict of system data
    """
    fact_comparison = _select_applicable_info(inventory_service_systems, fact_namespace)

    system_mappings = [_system_mapping(system) for system in inventory_service_systems]
    return {'facts': fact_comparison, 'systems': system_mappings}


def _select_applicable_info(systems, fact_namespace):
    """
    Take a list of systems with fact namespace, and output a "pivoted" list of
    facts, where each fact key has a dict of systems and their values. This is
    useful when comparing facts across systems.
    """
    # create dicts of id + info
    ids_and_info = [_system_facts_and_id(system, fact_namespace) for system in systems]

    # union the keys into one big set
    available_info_names = set()
    for fact_ids in ids_and_info:
        available_info_names |= fact_ids.keys()

    info_comparisons = [_create_comparison(ids_and_info, info_name)
                        for info_name in available_info_names
                        if info_name is not SYSTEM_ID_KEY]
    return info_comparisons


def _find_facts_for_namespace(system, fact_namespace):
    """
    return the facts for the given namespace
    """
    # TODO: we are assuming we just need to handle one namespace, and
    # that the namespace is always present.
    for facts in system['facts']:
        if facts['namespace'] == fact_namespace:
            dataframe = json_normalize(facts['facts'], sep='.')
            return dataframe.to_dict(orient='records')[0]


def _system_facts_and_id(system, fact_namespace):
    """
    Pull the system facts dict out from a system record and add the ID to the dict
    """
    facts_and_id = _find_facts_for_namespace(system, fact_namespace)
    facts_and_id[SYSTEM_ID_KEY] = system[SYSTEM_ID_KEY]
    return facts_and_id


def _create_comparison(systems, info_name):
    """
    Take an individual fact, search for it across all systems, and create a dict
    of each system's ID and fact value. Additionally, add a "state" field that
    says if all systems have the same values or different values.

    Note that when passing in "systems" to this method, the ID needs to be listed
    as a fact key.
    """
    info_comparison = COMPARISON_DIFFERENT

    system_id_values = [{'id': x['id'], 'value': x.get(info_name, "FACT_NOT_SET")} for x in systems]

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
    return {'id': system['id'], 'fqdn': system['fqdn'], 'last_updated': system['updated']}
