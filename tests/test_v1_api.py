import json

from flask import g


# needed to do deletes + creates
from historical_system_profiles import db_interface

from . import fixtures, utils


class HSPApiTests(utils.ApiTest):
    def test_status_bad_uuid(self):
        response = self.client.get(
            "/api/historical-system-profiles/v1/profiles/1",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("too short", json.loads(response.data)["detail"])

    def test_duplicate_uuid(self):
        response = self.client.get(
            "/api/historical-system-profiles/v1/profiles"
            "/9b4e0f4a-ab20-11ea-af1f-98fa9b07d419,9b4e0f4a-ab20-11ea-af1f-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEquals(
            "duplicate IDs requested: ['9b4e0f4a-ab20-11ea-af1f-98fa9b07d419']",
            response.json["message"],
        )

    def test_create_delete_hsp(self):
        # this test requires accessing some data via the DB interface. We don't
        # expose create or delete via the API.

        # confirm there are zero records to start
        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/6887d404-ab27-11ea-b3ae-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

        # add one record, confirm count
        with self.test_flask_app.app_context():
            db_interface.create_profile("6887d404-ab27-11ea-b3ae-98fa9b07d419", {}, "1234", "5678")

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/6887d404-ab27-11ea-b3ae-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEquals(1, len(data["data"][0]["profiles"]))

        # delete all records, confirm count
        with self.test_flask_app.app_context():
            db_interface.delete_hsps_by_inventory_id("6887d404-ab27-11ea-b3ae-98fa9b07d419")

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/6887d404-ab27-11ea-b3ae-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_missing_single_hsp(self):
        # get a 404 for a missing record
        response = self.client.get(
            "/api/historical-system-profiles/v1/profiles/d3b51a7a-ab27-11ea-a738-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_hsp_in_list(self):
        # get a 404 if one out of two records is missing
        with self.test_flask_app.app_context():
            db_interface.create_profile("eca1c5c4-ab27-11ea-958a-98fa9b07d419", {}, "1234", "5678")

        self.addInventoryRecord("eca1c5c4-ab27-11ea-958a-98fa9b07d419", "test_name")
        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/eca1c5c4-ab27-11ea-958a-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        valid_profile_id = data["data"][0]["profiles"][0]["id"]

        # NB: we are fetching individual profiles now, not the list of profiles for the system
        response = self.client.get(
            f"/api/historical-system-profiles/v1/profiles/{valid_profile_id}",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f"/api/historical-system-profiles/v1/profiles/{valid_profile_id}"
            ",9db484bc-ab2a-11ea-9a15-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json["message"],
            "ids [9db484bc-ab2a-11ea-9a15-98fa9b07d419] not available to display",
        )

    def test_filter_hsps_by_inventory_groups(self):
        with self.test_flask_app.app_context():
            g.rbac_filters = {"group.id": [{"id": "736bcb60-bbf5-4464-921f-1c431d76a124"}]}
            self.assertEqual(
                g.get("rbac_filters"),
                {"group.id": [{"id": "736bcb60-bbf5-4464-921f-1c431d76a124"}]},
            )

            for profile in fixtures.HSPS_WITH_DIFFERENT_GROUPS:
                self.addInventoryRecord(
                    profile["inventory_id"], "system_for_account_{}".format(profile["account"])
                )
                db_interface.create_profile(
                    profile["inventory_id"],
                    profile["system_profile"],
                    profile["account"],
                    profile["org_id"],
                    profile["groups"],
                )

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/30365ed4-19d8-4415-993e-1d430dc70ed7",
            headers=fixtures.AUTH_HEADER,
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(2, len(data["data"][0]["profiles"]))

    def test_pagination(self):
        # create inventory record
        self.addInventoryRecord(
            "16c1b34a-bf78-494e-ba3d-fe7dc1b18459",
            "pagination_test_system_display_name",
        )

        # create four profiles, iterating "some_fact" to simulate check-ins for this host
        # 1234 is the account number
        # 5678 is the org id
        with self.test_flask_app.app_context():
            for i in range(4):
                db_interface.create_profile(
                    "16c1b34a-bf78-494e-ba3d-fe7dc1b18459",
                    {"some_fact": f"some_value_{i}"},
                    "1234",
                    "5678",
                )

        # fetch the system profiles providing limit and offset
        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/16c1b34a-bf78-494e-ba3d-fe7dc1b18459"
            "?limit=2&offset=1",
            headers=fixtures.AUTH_HEADER,
        )

        returned_profiles = response.json["data"][0]["profiles"]

        # assert that the limit works
        self.assertEqual(len(returned_profiles), 2)

        # get the fact from a particular profile
        profile_id = returned_profiles[1]["id"]
        profile_response = self.client.get(
            f"/api/historical-system-profiles/v1/profiles/{profile_id}",
            headers=fixtures.AUTH_HEADER,
        )
        some_value = profile_response.json["data"][0]["system_profile"]["some_fact"]

        # assert that the offset works by comparing the fact for the profile in that position
        self.assertEqual(some_value, "some_value_1")
