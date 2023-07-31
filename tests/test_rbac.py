import unittest

import mock

from mock import MagicMock as mm

from kerlescan import view_helpers
from kerlescan.exceptions import HTTPError
from kerlescan.rbac_service_interface import get_rbac_filters


class RBACTests(unittest.TestCase):
    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.rbac_service_interface.fetch_url")
    def test_has_perm(self, mock_fetch_url, mock_get_key):
        mock_get_key.return_value = (
            "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMTIxMjcyOSIsICJ0eXBlIjogI"
            "lN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2xhc3NpYy1wcm94eSIsICJzeXN0ZW0iOiB7Im"
            "NuIjogIjIyY2Q4ZTM5LTEzYmItNGQwMi04MzE2LTg0Yjg1MGRjNTEzNiIsICJjZXJ0X3R"
            "5cGUiOiAic3lzdGVtIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjAwMDAwMSJ9fX0K"
        )
        mock_fetch_url.return_value = {"data": [{"permission": "myperm:*:*"}]}
        mock_request = mm()
        mock_request.path = "/some/path"
        self.assertIsNone(
            view_helpers.ensure_has_permission(
                permissions=[["myperm:*:*"]],
                application="app",
                app_name="app-name",
                request=mock_request,
                logger=mm(),
                request_metric=mm(),
                exception_metric=mm(),
            )
        )

    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.rbac_service_interface.fetch_url")
    def test_missing_perm(self, mock_fetch_url, mock_get_key):
        mock_get_key.return_value = (
            "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMTIxMjcyOSIsICJ0eXBlIjogI"
            "lN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2xhc3NpYy1wcm94eSIsICJzeXN0ZW0iOiB7Im"
            "NuIjogIjIyY2Q4ZTM5LTEzYmItNGQwMi04MzE2LTg0Yjg1MGRjNTEzNiIsICJjZXJ0X3R"
            "5cGUiOiAic3lzdGVtIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjAwMDAwMSJ9fX0K"
        )
        mock_fetch_url.return_value = {"data": [{"permission": "myperm:*:*"}]}
        mock_request = mm()
        mock_request.path = "/some/path"
        with self.assertRaises(HTTPError):
            view_helpers.ensure_has_permission(
                permissions=["r2:*:*"],
                application="app",
                app_name="app-name",
                request=mock_request,
                logger=mm(),
                request_metric=mm(),
                exception_metric=mm(),
            )

    def test_get_rbac_filters_no_inventory_permission(self):
        rbac_data = [
            {"resourceDefinitions": [], "permission": "advisor:*:*"},
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(rbac_filters, {"group.id": []})  # no hosts

    def test_get_rbac_filters_read_permisson_empty_resource(self):
        rbac_data = [
            {"resourceDefinitions": [], "permission": "inventory:hosts:read"},
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(rbac_filters, {"group.id": None})  # all hosts

    def test_get_rbac_filters_only_write_permisson(self):
        rbac_data = [
            {"resourceDefinitions": [], "permission": "inventory:groups:write"},
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(rbac_filters, {"group.id": []})  # no hosts

    def test_get_rbac_filters_read_permisson_not_relevant_resource(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "other.id",
                            "value": ["foo", "bar"],
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {"group.id": None},
        )  # all hosts

    def test_get_rbac_filters_read_permisson_no_value_resource(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {"group.id": None},
        )

    def test_get_rbac_filters_read_permisson_complex_resource(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": [
                                "df57820e-965c-49a6-b0bc-797b7dd60581",  # Group 1
                                "df3f0efd-c853-41b5-80a1-86881d5343d1",  # Group 2
                                None,  # No group (ungrouped hosts)
                            ],
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {
                "group.id": [
                    "df57820e-965c-49a6-b0bc-797b7dd60581",
                    "df3f0efd-c853-41b5-80a1-86881d5343d1",
                    None,
                ]
            },
        )

    def test_get_rbac_filters_multiple_read_permissons(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": [
                                "df57820e-965c-49a6-b0bc-797b7dd60581",  # Group 1
                            ],
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": [
                                "df3f0efd-c853-41b5-80a1-86881d5343d1",  # Group 2
                            ],
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {
                "group.id": [
                    "df57820e-965c-49a6-b0bc-797b7dd60581",
                    "df3f0efd-c853-41b5-80a1-86881d5343d1",
                ]
            },
        )

    def test_get_rbac_filters_with_all_groups_permissons(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": [
                                "df57820e-965c-49a6-b0bc-797b7dd60581",  # Group 1
                            ],
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {"group.id": None},
        )

    def test_get_rbac_filters_value_string(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": "df57820e-965c-49a6-b0bc-797b7dd60581,df3f0efd-c853-41b5-80a1-86881d5343d1",
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {
                "group.id": [
                    "df57820e-965c-49a6-b0bc-797b7dd60581",
                    "df3f0efd-c853-41b5-80a1-86881d5343d1",
                ]
            },
        )

    def test_get_rbac_filters_value_string_with_null(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": "df57820e-965c-49a6-b0bc-797b7dd60581,df3f0efd-c853-41b5-80a1-86881d5343d1,null",
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        rbac_filters = get_rbac_filters(rbac_data)
        self.assertEqual(
            rbac_filters,
            {
                "group.id": [
                    "df57820e-965c-49a6-b0bc-797b7dd60581",
                    "df3f0efd-c853-41b5-80a1-86881d5343d1",
                    None,
                ]
            },
        )

    def test_get_rbac_filters_value_unsupported(self):
        rbac_data = [
            {
                "resourceDefinitions": [
                    {
                        "attributeFilter": {
                            "key": "group.id",
                            "value": {},
                            "operation": "in",
                        }
                    }
                ],
                "permission": "inventory:hosts:read",
            },
        ]
        self.assertRaises(TypeError, get_rbac_filters, rbac_data)
