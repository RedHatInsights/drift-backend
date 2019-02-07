import json
import os
import requests
from urllib.parse import urljoin

from drift.exceptions import SystemNotReturned

AUTH_HEADER_NAME = 'X-RH-IDENTITY'
INVENTORY_SVC_HOSTNAME = os.getenv('INVENTORY_SVC_URL', "http://inventory_svc_url_is_not_set")
INVENTORY_SVC_HOSTS_ENDPOINT = '/r/insights/platform/inventory/api/v1/hosts/%s?per_page=%s'

MAX_UUID_COUNT = 20


def get_key_from_headers(incoming_headers):
    return incoming_headers.get(AUTH_HEADER_NAME)


def fetch_systems(system_ids, service_auth_key):
    if len(system_ids) > MAX_UUID_COUNT:
        raise SystemNotReturned("Too many systems requested, limit is %s" % MAX_UUID_COUNT)

    auth_header = {AUTH_HEADER_NAME: service_auth_key}

    inventory_service_location = urljoin(INVENTORY_SVC_HOSTNAME, INVENTORY_SVC_HOSTS_ENDPOINT)
    response = requests.get(inventory_service_location % (','.join(system_ids), MAX_UUID_COUNT),
                            headers=auth_header)
    result = json.loads(response.text)

    if result['count'] < len(system_ids):
        system_ids_returned = {system['id'] for system in result['results']}
        missing_ids = set(system_ids) - system_ids_returned
        raise SystemNotReturned("System(s) %s not available to display" % ','.join(missing_ids))
    return result['results']
