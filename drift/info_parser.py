SYSTEM_ID = 'id'
FACT_NAMESPACE = 'inventory'


def build_comparisons(inventory_service_systems):
    """
    given a list of system dicts, return a dict of comparisons, along with a dict of metadata.
    """
    fact_comparison = _select_applicable_info(inventory_service_systems)

    metadata = [_system_metadata(system) for system in inventory_service_systems]
    return {'facts': fact_comparison, 'metadata': metadata}


def _select_applicable_info(systems):
    """
    Take a list of systems, and output a "pivoted" list of facts, where each fact
    key has a dict of systems and their values. This is useful when comparing
    facts across systems.
    """
    # create dicts of id + info
    ids_and_info = [_system_facts_and_id(system) for system in systems]

    # TODO: we are assuming all info keys exist for each system. This is not a good assumption
    available_info_names = ids_and_info[0].keys()

    info_comparisons = [_create_comparison(ids_and_info, info_name)
                        for info_name in available_info_names
                        if info_name is not SYSTEM_ID]
    return info_comparisons


def _find_facts_for_namespace(system, namespace):
    """
    return the facts for the given namespace
    """
    for facts in system['facts']:
        if facts['namespace'] == namespace:
            return facts['facts']


def _system_facts_and_id(system):
    """
    Pull the system facts dict out from a system record and add the ID to the dict
    """
    # TODO: we are assuming we just need to handle one namespace, and
    # that the namespace is always present.
    facts_and_id = _find_facts_for_namespace(system, FACT_NAMESPACE)
    facts_and_id[SYSTEM_ID] = system[SYSTEM_ID]
    return facts_and_id


def _create_comparison(systems, info_name):
    """
    Take an individual fact, search for it across all systems, and create a dict
    of each system's ID and fact value. Additionally, add a "state" field that
    says if all systems have the same values or different values.

    Note that when passing in "systems" to this method, the ID needs to be listed
    as a fact key.
    """
    info_comparison = 'DIFFERENT'

    system_values = {x['id']: x[info_name] for x in systems}

    # map the info values down to a set. This lets us check cardinality for sameness.
    if len({system[info_name] for system in systems}) == 1:
        info_comparison = 'SAME'

    return {'name': info_name, 'state': info_comparison, 'systems': system_values}


def _system_metadata(system):
    """
    create a metadata field for one system
    """
    return {'id': system['id'], 'fqdn': system['fqdn'], 'last_updated': system['updated']}
