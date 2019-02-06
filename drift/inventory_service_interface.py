import json
import os
import requests
from urllib.parse import urljoin

from drift.exceptions import SystemNotReturned

AUTH_HEADER_NAME = 'X-RH-IDENTITY'
INVENTORY_SVC_HOSTNAME = os.getenv('INVENTORY_SVC_URL', "http://inventory_svc_url_is_not_set")
INVENTORY_SVC_HOSTS_ENDPOINT = '/r/insights/platform/inventory/api/v1/hosts/%s'


def get_key_from_headers(incoming_headers):
    return incoming_headers.get(AUTH_HEADER_NAME)


def fetch_systems(system_ids, service_auth_key):
    auth_header = {AUTH_HEADER_NAME: service_auth_key}
    systems = []

    inventory_service_location = urljoin(INVENTORY_SVC_HOSTNAME, INVENTORY_SVC_HOSTS_ENDPOINT)
    for system_id in system_ids:
        response = requests.get(inventory_service_location % system_id, headers=auth_header)
        result = json.loads(response.text)
        if result['count'] == 0:
            raise SystemNotReturned("System %s not available to display" % system_id)
        systems.append(result['results'][0])

    # TODO: see if we need to ensure we got back the number of systems we expected
    return systems
