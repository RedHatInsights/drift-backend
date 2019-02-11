import requests
import responses
import string
import unittest
import mock

from drift import app, inventory_service_interface
from drift.exceptions import InventoryServiceError, SystemNotReturned
from . import fixtures


class InventoryServiceTests(unittest.TestCase):

    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.mock_logger = mock.Mock()

    def _create_response_for_systems(self, service_hostname, system_uuids):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, system_uuids),
                      body=fixtures.SYSTEMS_TEMPLATE, status=requests.codes.ok,
                      content_type='application/json')

    def _create_500_response_for_systems(self, service_hostname, system_uuids):
        url_template = "http://%s/r/insights/platform/inventory/api/v1/hosts/%s"
        responses.add(responses.GET, url_template % (service_hostname, system_uuids),
                      body="I am error", status=requests.codes.INTERNAL_SERVER_ERROR,
                      content_type='application/json')

    @responses.activate
    def test_fetch_systems(self):
        systems_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                            '264fb5b2-262f-11e9-9b12-c85b761454fa']

        self._create_response_for_systems('inventory_svc_url_is_not_set',
                                          ','.join(systems_to_fetch))

        systems = inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key",
                                                            self.mock_logger)

        found_system_ids = {system['id'] for system in systems}
        self.assertSetEqual(found_system_ids, set(systems_to_fetch))

    @responses.activate
    def test_fetch_systems_missing_system(self):
        systems_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                            '264fb5b2-262f-11e9-9b12-c85b761454fa',
                            '269a3da8-262f-11e9-8ee5-c85b761454fa']

        self._create_response_for_systems('inventory_svc_url_is_not_set',
                                          ','.join(systems_to_fetch))

        with self.assertRaises(SystemNotReturned) as cm:
            inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key",
                                                      self.mock_logger)

        self.assertEqual(cm.exception.message,
                         "System(s) 269a3da8-262f-11e9-8ee5-c85b761454fa not available to display")

    @responses.activate
    def test_fetch_systems_backend_service_error(self):
        systems_to_fetch = ['243926fa-262f-11e9-a632-c85b761454fa',
                            '264fb5b2-262f-11e9-9b12-c85b761454fa',
                            '269a3da8-262f-11e9-8ee5-c85b761454fa']

        self._create_500_response_for_systems('inventory_svc_url_is_not_set',
                                              ','.join(systems_to_fetch))

        with self.assertRaises(InventoryServiceError) as cm:
            inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key",
                                                      self.mock_logger)

        self.assertEqual(cm.exception.message,
                         "Error received from backend service")

    def test_fetch_too_many_systems(self):
        systems_to_fetch = list(string.ascii_lowercase)

        with self.assertRaises(SystemNotReturned) as cm:
            inventory_service_interface.fetch_systems(systems_to_fetch, "my-auth-key",
                                                      self.mock_logger)

        self.assertEqual(cm.exception.message,
                         "Too many systems requested, limit is 20")
