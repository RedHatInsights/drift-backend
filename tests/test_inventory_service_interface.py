import responses

from drift import inventory_service_interface
from drift.exceptions import SystemNotReturned

import unittest

from . import fixtures


class InventoryServiceTests(unittest.TestCase):

    def _create_response_for_system(self, service_hostname, system_uuid):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, system_uuid),
                      body=fixtures.SYSTEM_TEMPLATE % system_uuid, status=200,
                      content_type='application/json')

    def _create_response_for_missing_system(self, service_hostname, system_uuid):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, system_uuid),
                      body=fixtures.SYSTEM_NOT_FOUND_TEMPLATE, status=200,
                      content_type='application/json')

    @responses.activate
    def test_fetch_systems(self):
        systems_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                            '264fb5b2-262f-11e9-9b12-c85b761454fa',
                            '269a3da8-262f-11e9-8ee5-c85b761454fa']

        for system_id in systems_to_fetch:
            self._create_response_for_system('inventory_svc_url_is_not_set', system_id)

        systems = inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key")

        found_system_ids = {system['id'] for system in systems}
        self.assertSetEqual(found_system_ids, set(systems_to_fetch))

    @responses.activate
    def test_fetch_systems_missing_system(self):
        systems_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                            '264fb5b2-262f-11e9-9b12-c85b761454fa',
                            '269a3da8-262f-11e9-8ee5-c85b761454fa']

        self._create_response_for_system('inventory_svc_url_is_not_set',
                                         '243926fa-262f-11e9-a632-c85b761454fa')
        self._create_response_for_missing_system('inventory_svc_url_is_not_set',
                                                 '264fb5b2-262f-11e9-9b12-c85b761454fa')
        self._create_response_for_system('inventory_svc_url_is_not_set',
                                         '269a3da8-262f-11e9-8ee5-c85b761454fa')

        with self.assertRaises(SystemNotReturned) as cm:
            inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key")

        self.assertEqual(cm.exception.message,
                         "System 264fb5b2-262f-11e9-9b12-c85b761454fa not available to display")
