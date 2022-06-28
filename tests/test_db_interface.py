import json

from historical_system_profiles import db_interface

from . import fixtures, utils


class DBInterfaceTests(utils.ApiTest):
    # TODO: this should rely only on the DB interface and not make any rest calls
    def test_save_model(self):
        # confirm there are zero records associated with an inventory ID
        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

        # add one record, confirm count
        with self.test_flask_app.app_context():
            # NB: this is an INVENTORY id, not HSP id! HSP ids are generated at creation time.
            db_interface.create_profile("29dbe6ce-897f-11ea-8f75-98fa9b07d419", {}, "1234", "5678")

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEquals(1, len(data["data"][0]["profiles"]))

        # delete all records, confirm count
        with self.test_flask_app.app_context():
            # inventory ID is the only way to reference records to delete
            db_interface.delete_hsps_by_inventory_id("29dbe6ce-897f-11ea-8f75-98fa9b07d419")

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
