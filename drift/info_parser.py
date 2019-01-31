DRIFT_FACTS = {'bios_uuid', 'display_name'}
DRIFT_HOST_ID = {'id'}


def build_comparisons(inventory_service_hosts):
    """
    given a list of host dicts, return a dict of comparisons, along with a dict of metadata.
    """
    fact_comparison = _select_applicable_info(DRIFT_FACTS, inventory_service_hosts)

    metadata = [_host_metadata(host) for host in inventory_service_hosts]
    return {'facts': fact_comparison, 'metadata': metadata}


def _select_applicable_info(info_keys, hosts):
    """
    Take a list of hosts, and output a "pivoted" list of facts, where each fact
    key has a dict of hosts and their values. This is useful when comparing
    facts across hosts.
    """
    # create dicts of host + info
    ids_and_info = [{key: host[key] for key in (info_keys | DRIFT_HOST_ID & host.keys())}
                    for host in hosts]

    # TODO: we are assuming all info keys exist for each host. This is not a good assumption
    available_info_names = ids_and_info[0].keys()

    info_comparisons = [_create_comparison(ids_and_info, info_name)
                        for info_name in available_info_names
                        if info_name in info_keys]
    return info_comparisons


def _create_comparison(hosts, info_name):
    """
    Take an individual fact, search for it across all hosts, and create a dict
    of each host's ID and fact value. Additionally, add a "status" field that
    says if all hosts have the same values or different values.

    Note that when passing in "hosts" to this method, the ID needs to be listed
    as a fact key.
    """
    info_comparison = 'DIFFERENT'

    host_values = {x['id']: x[info_name] for x in hosts}

    # map the info values down to a set. This lets us check cardinality for sameness.
    if len({x[info_name] for x in hosts}) == 1:
        info_comparison = 'SAME'

    return {'name': info_name, 'status': info_comparison, 'hosts': host_values}


def _host_metadata(host):
    """
    create a metadata field for one host
    """
    return {'id': host['id'], 'fqdn': host['fqdn'], 'last_updated': host['updated']}
