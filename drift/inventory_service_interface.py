import json
import requests
from urllib.parse import urljoin

from drift import config
from drift.constants import AUTH_HEADER_NAME, INVENTORY_SVC_HOSTS_ENDPOINT, MAX_UUID_COUNT
from drift.exceptions import SystemNotReturned, InventoryServiceError
from drift.mock_data import mock_data


def get_key_from_headers(incoming_headers):
    """
    return auth key from header
    """
    return incoming_headers.get(AUTH_HEADER_NAME)


def fetch_systems(system_ids, service_auth_key, logger):
    """
    fetch systems from inventory service
    """
    if len(system_ids) > MAX_UUID_COUNT:
        raise SystemNotReturned("Too many systems requested, limit is %s" % MAX_UUID_COUNT)

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    inventory_service_location = urljoin(config.inventory_svc_hostname,
                                         INVENTORY_SVC_HOSTS_ENDPOINT)
    response = requests.get(inventory_service_location % (','.join(system_ids), MAX_UUID_COUNT),
                            headers=auth_header)

    if response.status_code is not requests.codes.ok:
        logger.warn("%s error received from inventory service: %s" %
                    (response.status_code, response.text))
        raise InventoryServiceError("Error received from backend service")

    result = json.loads(response.text)

    if result['count'] < len(system_ids):
        system_ids_returned = {system['id'] for system in result['results']}
        missing_ids = set(system_ids) - system_ids_returned
        raise SystemNotReturned("System(s) %s not available to display" % ','.join(missing_ids))

    if config.return_mock_data:
        for system in result['results']:
            mock_facts = mock_data.fetch_mock_facts(system['id'])
            system['facts'].append(mock_facts)

    return result['results']
