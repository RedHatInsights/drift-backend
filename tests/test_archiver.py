from . import fixtures
from . import utils

from historical_system_profiles import archiver, db_interface

import mock
from mock import MagicMock


class ArchiverTests(utils.ApiTest):
    @mock.patch("historical_system_profiles.archiver._check_and_send_notifications")
    def test_archive_profile(self, mock_check_and_send):
        mock_check_and_send.return_value = None
        message = MagicMock()
        message.value = fixtures.EVENT_MESSAGE_VALUE
        with self.test_flask_app.app_context():
            # save the same profile twice on purpose
            archiver._archive_profile(message, MagicMock(), MagicMock(), MagicMock())
            archiver._archive_profile(message, MagicMock(), MagicMock(), MagicMock())

        hsps = []
        with self.test_flask_app.app_context():
            hsps = db_interface.get_hsps_by_inventory_id(
                "6388350e-b18d-11ea-ad7f-98fa9b07d419", "5432", "10", "0"
            )

        # ensure we didnt save the duplicate
        self.assertEquals(1, len(hsps))

        # cleanup
        with self.test_flask_app.app_context():
            db_interface.delete_hsps_by_inventory_id(
                "6388350e-b18d-11ea-ad7f-98fa9b07d419"
            )
