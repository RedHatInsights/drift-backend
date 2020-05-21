import requests
import responses
import unittest
import mock

from drift import app
from kerlescan import inventory_service_interface
from kerlescan.exceptions import ServiceError, ItemNotReturned
from . import fixtures


class InventoryServiceTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.mock_logger = mock.Mock()

        self.mock_counters = {
            "systems_compared_no_sysprofile": mock.MagicMock(),
            "inventory_service_requests": mock.MagicMock(),
            "inventory_service_exceptions": mock.MagicMock(),
        }

    def _create_response_for_systems(self, service_hostname, system_uuids):
        url_template = "http://%s/api/inventory/v1/hosts/%s"
        responses.add(
            responses.GET,
            url_template % (service_hostname, system_uuids),
            body=fixtures.FETCH_SYSTEMS_INV_SVC,
            status=requests.codes.ok,
            content_type="application/json",
        )

    def _create_response_for_system_profiles(self, service_hostname, system_uuids):
        url_template = "http://%s/api/inventory/v1/hosts/%s/system_profile"
        responses.add(
            responses.GET,
            url_template % (service_hostname, system_uuids),
            body=fixtures.FETCH_SYSTEM_PROFILES_INV_SVC,
            status=requests.codes.ok,
            content_type="application/json",
        )

    def _create_500_response_for_systems(self, service_hostname, system_uuids):
        url_template = "http://%s/api/inventory/v1/hosts/%s"
        responses.add(
            responses.GET,
            url_template % (service_hostname, system_uuids),
            body="I am error",
            status=requests.codes.INTERNAL_SERVER_ERROR,
            content_type="application/json",
        )

    def _create_500_response_for_system_profiles(self, service_hostname, system_uuids):
        url_template = "http://%s/api/inventory/v1/hosts/%s/system_profile"
        responses.add(
            responses.GET,
            url_template % (service_hostname, system_uuids),
            body="I am error",
            status=requests.codes.INTERNAL_SERVER_ERROR,
            content_type="application/json",
        )

    @responses.activate
    def test_fetch_systems_with_profiles(self):
        systems_to_fetch = [
            "243926fa-262f-11e9-a632-c85b761454fa",
            "264fb5b2-262f-11e9-9b12-c85b761454fa",
        ]

        self._create_response_for_systems(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )
        self._create_response_for_system_profiles(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )

        systems = inventory_service_interface.fetch_systems_with_profiles(
            systems_to_fetch, "my-auth-key", self.mock_logger, self.mock_counters
        )
        found_system_ids = {system["id"] for system in systems}
        self.assertSetEqual(found_system_ids, set(systems_to_fetch))

    @responses.activate
    def test_fetch_systems_missing_system(self):
        systems_to_fetch = [
            "243926fa-262f-11e9-a632-c85b761454fa",
            "264fb5b2-262f-11e9-9b12-c85b761454fa",
            "269a3da8-262f-11e9-8ee5-c85b761454fa",
        ]

        self._create_response_for_systems(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )

        self._create_response_for_system_profiles(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )

        with self.assertRaises(ItemNotReturned) as cm:
            inventory_service_interface.fetch_systems_with_profiles(
                systems_to_fetch, "my-auth-key", self.mock_logger, self.mock_counters
            )

        self.assertEqual(
            cm.exception.message,
            "ids [269a3da8-262f-11e9-8ee5-c85b761454fa] not available to display",
        )

    @responses.activate
    def test_fetch_systems_backend_service_error(self):
        systems_to_fetch = [
            "243926fa-262f-11e9-a632-c85b761454fa",
            "264fb5b2-262f-11e9-9b12-c85b761454fa",
            "269a3da8-262f-11e9-8ee5-c85b761454fa",
        ]

        self._create_500_response_for_systems(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )

        self._create_500_response_for_system_profiles(
            "inventory_svc_url_is_not_set", ",".join(systems_to_fetch)
        )

        with self.assertRaises(ServiceError) as cm:
            inventory_service_interface.fetch_systems_with_profiles(
                systems_to_fetch, "my-auth-key", self.mock_logger, self.mock_counters
            )

        self.assertEqual(cm.exception.message, "Error received from backend service")
