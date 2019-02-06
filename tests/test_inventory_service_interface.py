import responses

from drift import inventory_service_interface
from drift.exceptions import SystemNotReturned

import unittest

from . import fixtures


class InventoryServiceTests(unittest.TestCase):

    def _create_response_for_host(self, service_hostname, host_uuid):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, host_uuid),
                      body=fixtures.HOST_TEMPLATE % host_uuid, status=200,
                      content_type='application/json')

    def _create_response_for_missing_host(self, service_hostname, host_uuid):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, host_uuid),
                      body=fixtures.HOST_NOT_FOUND_TEMPLATE, status=200,
                      content_type='application/json')

    @responses.activate
    def test_fetch_hosts(self):
        hosts_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                          '264fb5b2-262f-11e9-9b12-c85b761454fa',
                          '269a3da8-262f-11e9-8ee5-c85b761454fa']

        for host_id in hosts_to_fetch:
            self._create_response_for_host('inventory_svc_url_is_not_set', host_id)

        hosts = inventory_service_interface.fetch_hosts(hosts_to_fetch, "my-auth-key")

        found_host_ids = {host['id'] for host in hosts}
        self.assertSetEqual(found_host_ids, set(hosts_to_fetch))

    @responses.activate
    def test_fetch_hosts_missing_host(self):
        hosts_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                          '264fb5b2-262f-11e9-9b12-c85b761454fa',
                          '269a3da8-262f-11e9-8ee5-c85b761454fa']

        self._create_response_for_host('inventory_svc_url_is_not_set',
                                       '243926fa-262f-11e9-a632-c85b761454fa')
        self._create_response_for_missing_host('inventory_svc_url_is_not_set',
                                               '264fb5b2-262f-11e9-9b12-c85b761454fa')
        self._create_response_for_host('inventory_svc_url_is_not_set',
                                       '269a3da8-262f-11e9-8ee5-c85b761454fa')

        with self.assertRaises(SystemNotReturned) as cm:
            inventory_service_interface.fetch_hosts(hosts_to_fetch, "my-auth-key")

        self.assertEqual(cm.exception.message,
                         "System 264fb5b2-262f-11e9-9b12-c85b761454fa not available to display")
