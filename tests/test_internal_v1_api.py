import json
import uuid

from system_baseline import app

import unittest
from mock import patch
from . import fixtures


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.rbac_patcher = patch(
            "system_baseline.views.v1.view_helpers.ensure_has_permission"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def stopPatches(self):
        self.rbac_patcher.stop()


class ApiSystemsAssociationTests(ApiTest):
    def setUp(self):
        super(ApiSystemsAssociationTests, self).setUp()
        self.client.post(
            "api/system-baseline/v1/baselines",
            headers=fixtures.AUTH_HEADER,
            json=fixtures.BASELINE_ONE_LOAD,
        )

        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.baseline_id = [b["id"] for b in result["data"]][0]

        self.system_ids = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ]

        response = self.client.post(
            "api/system-baseline/v1/baselines/" + self.baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
            json={"system_ids": self.system_ids},
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        super(ApiSystemsAssociationTests, self).tearDown()

        # get all baselines
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        baselines = json.loads(response.data)["data"]

        for baseline in baselines:
            # get systems for baseline
            response = self.client.get(
                "api/system-baseline/v1/baselines/" + baseline["id"] + "/systems",
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

            system_ids = json.loads(response.data)["system_ids"]

            # delete systems
            response = self.client.post(
                "api/system-baseline/v1/baselines/"
                + baseline["id"]
                + "/systems/deletion_request",
                headers=fixtures.AUTH_HEADER,
                json={"system_ids": system_ids},
            )
            self.assertEqual(response.status_code, 200)

            # delete baseline
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_list_systems_with_baseline(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines/" + self.baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_system_ids = json.loads(response.data)["system_ids"]
        self.assertEqual(len(response_system_ids), 3)

        for system_id in self.system_ids:
            self.assertIn(system_id, response_system_ids)

    def test_delete_systems_with_baseline(self):
        # to delete
        system_ids = [
            self.system_ids[0],
            self.system_ids[1],
        ]

        # delete systems
        response = self.client.post(
            "api/system-baseline/v1/baselines/"
            + self.baseline_id
            + "/systems/deletion_request",
            headers=fixtures.AUTH_HEADER,
            json={"system_ids": system_ids},
        )
        self.assertEqual(response.status_code, 200)

        # read what systems persisted
        response = self.client.get(
            "api/system-baseline/v1/baselines/" + self.baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_system_ids = json.loads(response.data)
        self.assertEqual(len(response_system_ids), 1)

    def test_delete_nonexistent_system(self):
        # to delete
        system_ids = [
            str(uuid.uuid4()),
        ]

        # delete systems
        response = self.client.post(
            "api/system-baseline/v1/baselines/"
            + self.baseline_id
            + "/systems/deletion_request",
            headers=fixtures.AUTH_HEADER,
            json=system_ids,
        )
        self.assertEqual(response.status_code, 400)

        # read what systems persisted
        response = self.client.get(
            "api/system-baseline/v1/baselines/" + self.baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_system_ids = json.loads(response.data)["system_ids"]
        self.assertEqual(len(response_system_ids), 3)

    def test_adding_few_systems(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        baseline_id = [b["id"] for b in result["data"]][0]

        # to create
        system_ids = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ]

        response = self.client.post(
            "api/system-baseline/v1/baselines/" + baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
            json={"system_ids": system_ids},
        )
        self.assertEqual(response.status_code, 200)

        response_system_ids = json.loads(response.data)["system_ids"]
        self.assertEqual(len(response_system_ids), 5)

        for system_id in system_ids:
            self.assertIn(system_id, response_system_ids)

    def test_deleting_systems_by_id(self):
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        baseline_id = [b["id"] for b in result["data"]][0]

        # to create
        system_ids = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ]

        response = self.client.post(
            "api/system-baseline/v1/baselines/" + baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
            json={"system_ids": system_ids},
        )
        self.assertEqual(response.status_code, 200)

        system_ids_to_delete = system_ids[0:2]
        system_ids_to_remain = system_ids[2:]

        response = self.client.delete(
            "api/system-baseline/internal/v1/systems/%s"
            % ",".join(system_ids_to_delete),
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        # read what systems persisted
        response = self.client.get(
            "api/system-baseline/v1/baselines/" + baseline_id + "/systems",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_system_ids = json.loads(response.data)["system_ids"]

        # deleted systems
        for system_id in system_ids_to_delete:
            self.assertNotIn(system_id, response_system_ids)

        # remaining systems
        for system_id in system_ids_to_remain:
            self.assertIn(system_id, response_system_ids)


class InternalApiBaselinesTests(ApiTest):
    def setUp(self):
        super(InternalApiBaselinesTests, self).setUp()
        for baseline_load in [
            fixtures.BASELINE_ONE_LOAD,
            fixtures.BASELINE_TWO_LOAD,
            fixtures.BASELINE_UNSORTED_LOAD,
        ]:
            response = self.client.post(
                "api/system-baseline/v1/baselines",
                headers=fixtures.AUTH_HEADER,
                json=baseline_load,
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.baseline_ids = [b["id"] for b in result["data"]]
        self.assertEqual(len(self.baseline_ids), 3)

    def tearDown(self):
        super(InternalApiBaselinesTests, self).tearDown()
        response = self.client.get(
            "api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER
        )
        data = json.loads(response.data)["data"]
        for baseline in data:
            # get systems for baseline
            response = self.client.get(
                "api/system-baseline/v1/baselines/" + baseline["id"] + "/systems",
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

            system_ids = json.loads(response.data)

            # delete systems
            response = self.client.post(
                "api/system-baseline/v1/baselines/"
                + baseline["id"]
                + "/systems/deletion_request",
                headers=fixtures.AUTH_HEADER,
                json=system_ids,
            )
            self.assertEqual(response.status_code, 200)

            # delete baseline
            response = self.client.delete(
                "api/system-baseline/v1/baselines/%s" % baseline["id"],
                headers=fixtures.AUTH_HEADER,
            )
            self.assertEqual(response.status_code, 200)

    def test_no_baselines_by_system_id(self):
        system_id = str(uuid.uuid4())

        response = self.client.get(
            "api/system-baseline/internal/v1/baselines",
            query_string={"system_id": system_id},
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_baseline_ids = json.loads(response.data)
        self.assertEqual(len(response_baseline_ids), 0)

    def test_one_baseline_by_system_id(self):
        system_id = str(uuid.uuid4())
        baseline_ids = self.baseline_ids[0:1]

        for baseline_id in baseline_ids:
            response = self.client.post(
                "api/system-baseline/v1/baselines/" + baseline_id + "/systems",
                headers=fixtures.AUTH_HEADER,
                json={"system_ids": [system_id]},
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "api/system-baseline/internal/v1/baselines",
            query_string={"system_id": system_id},
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_baseline_ids = json.loads(response.data)
        self.assertEqual(len(response_baseline_ids), len(baseline_ids))

    def test_few_baselines_by_system_id(self):
        system_id = str(uuid.uuid4())
        baseline_ids = self.baseline_ids[0:2]

        for baseline_id in baseline_ids:
            response = self.client.post(
                "api/system-baseline/v1/baselines/" + baseline_id + "/systems",
                headers=fixtures.AUTH_HEADER,
                json={"system_ids": [system_id]},
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "api/system-baseline/internal/v1/baselines",
            query_string={"system_id": system_id},
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response_baseline_ids = json.loads(response.data)
        self.assertEqual(len(response_baseline_ids), len(baseline_ids))
