import unittest
import uuid

from flask import Flask

from system_baseline import db_config
from system_baseline.models import SystemBaseline, SystemBaselineMappedSystem, db


baseline_facts = [
    {"name": "arch", "value": "x86_64"},
    {"name": "phony.arch.fact", "value": "some value"},
]
account1 = "00000001"
account2 = "00000002"
org_id1 = "10000001"
org_id2 = "10000002"

baseline_id1 = uuid.uuid4()
baseline_id2 = uuid.uuid4()
baseline_id3 = uuid.uuid4()
baseline_id4 = uuid.uuid4()
baseline_with_systems_with_groups = uuid.uuid4()

system_id1 = uuid.uuid4()
system_id2 = uuid.uuid4()
system_id3 = uuid.uuid4()
system_id4 = uuid.uuid4()
system_id5 = uuid.uuid4()
system_id6 = uuid.uuid4()
system_id7 = uuid.uuid4()
system_id8 = uuid.uuid4()
system_id9 = uuid.uuid4()


class DbModelTest(unittest.TestCase):
    def setUp(self):
        test_app = self._create_app()
        test_app.app_context().push()
        # make sure any open transactions are rolled back and then
        # close the session
        db.session.remove()
        # now drop the tables and recreate them - start fresh!
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()

    def _create_app(self):
        app = Flask(__name__)
        # set up DB
        app.config["SQLALCHEMY_ECHO"] = False
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = db_config.db_uri
        app.config["SQLALCHEMY_POOL_SIZE"] = db_config.db_pool_size
        app.config["SQLALCHEMY_POOL_TIMEOUT"] = db_config.db_pool_timeout
        db.init_app(app)
        return app

    def populate_db_with_stuff(self):
        rows = [
            SystemBaseline(
                account=account1,
                org_id=org_id1,
                id=baseline_id1,
                display_name="baseline1",
                baseline_facts=baseline_facts,
                mapped_systems=[
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id1,
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id2,
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id3,
                    ),
                ],
            ),
            SystemBaseline(
                account=account1,
                org_id=org_id1,
                id=baseline_id2,
                display_name="baseline2",
                baseline_facts=baseline_facts,
                mapped_systems=[
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id4,
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id5,
                    ),
                ],
            ),
            SystemBaseline(
                account=account2,
                org_id=org_id2,
                id=baseline_id3,
                display_name="baseline3",
                baseline_facts=baseline_facts,
                mapped_systems=[
                    SystemBaselineMappedSystem(
                        account=account2,
                        org_id=org_id2,
                        system_id=system_id6,
                    ),
                    SystemBaselineMappedSystem(
                        account=account2,
                        org_id=org_id2,
                        system_id=system_id7,
                    ),
                ],
            ),
            SystemBaseline(
                account=account2,
                org_id=org_id2,
                id=baseline_id4,
                display_name="baseline4",
                baseline_facts=baseline_facts,
                mapped_systems=[
                    SystemBaselineMappedSystem(
                        account=account2,
                        org_id=org_id2,
                        system_id=system_id6,
                    ),
                    SystemBaselineMappedSystem(
                        account=account2,
                        org_id=org_id2,
                        system_id=system_id8,
                    ),
                    SystemBaselineMappedSystem(
                        account=account2,
                        org_id=org_id2,
                        system_id=system_id9,
                    ),
                ],
            ),
        ]
        db.session.add_all(rows)
        db.session.commit()


class SystemBaselineTest(DbModelTest):
    def test_one_baseline(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        results = query.all()
        self.assertEqual(results[0].display_name, "baseline1")
        self.assertEqual(results[0].account, account1)
        self.assertEqual(results[0].org_id, org_id1)

    def test_another_baseline(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        results = query.all()
        self.assertEqual(results[0].display_name, "baseline1")
        self.assertEqual(results[0].account, account1)
        self.assertEqual(results[0].org_id, org_id1)


class SystemBaselineNotificationEnabledTest(DbModelTest):
    def test_of_default(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline with default notifications enabled",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        db.session.commit()
        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        result = query.one().notifications_enabled
        self.assertEqual(result, True)


class SystemBaselineMappedSystemTest(DbModelTest):
    def test_add_mapped_system(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        new_uuid = str(uuid.uuid4())
        baseline.add_mapped_system(new_uuid)
        db.session.add(baseline)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 1)
        self.assertEqual(result.mapped_system_ids()[0], new_uuid)

    def test_add_multiple_mapped_systems(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        db.session.commit()
        test_system_ids = []
        for i in range(4):
            test_system_id = str(uuid.uuid4())
            test_system_ids.append(test_system_id)
            baseline.add_mapped_system(test_system_id)
            db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 4)
        for test_system_id in test_system_ids:
            self.assertIn(test_system_id, result.mapped_system_ids())

    def test_remove_mapped_system(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        test_system_ids = []
        for i in range(4):
            test_system_id = str(uuid.uuid4())
            test_system_ids.append(test_system_id)
            baseline.add_mapped_system(test_system_id)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 4)
        removed_system_id = test_system_ids.pop(2)
        result.remove_mapped_system(removed_system_id)
        self.assertNotIn(removed_system_id, result.mapped_system_ids())
        db.session.commit()
        self.assertNotIn(removed_system_id, result.mapped_system_ids())

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 3)
        for test_system_id in test_system_ids:
            self.assertIn(test_system_id, result.mapped_system_ids())
        self.assertNotIn(removed_system_id, result.mapped_system_ids())

    def test_rollback_removed_mapped_system(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        test_system_ids = []
        for i in range(4):
            test_system_id = str(uuid.uuid4())
            test_system_ids.append(test_system_id)
            baseline.add_mapped_system(test_system_id)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 4)
        removed_system_id = test_system_ids.pop(2)
        result.remove_mapped_system(removed_system_id)
        self.assertNotIn(removed_system_id, result.mapped_system_ids())
        db.session.rollback()
        self.assertIn(removed_system_id, result.mapped_system_ids())

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 4)
        for test_system_id in test_system_ids:
            self.assertIn(test_system_id, result.mapped_system_ids())
        self.assertIn(removed_system_id, result.mapped_system_ids())

    def test_remove_mapped_system_not_in_list(self):
        baseline = SystemBaseline(
            account=account1,
            org_id=org_id1,
            display_name="baseline1",
            baseline_facts=baseline_facts,
        )
        db.session.add(baseline)
        test_system_ids = []
        for i in range(4):
            test_system_id = str(uuid.uuid4())
            test_system_ids.append(test_system_id)
            baseline.add_mapped_system(test_system_id)
        db.session.commit()

        query = SystemBaseline.query.filter(SystemBaseline.account == account1)
        self.assertEqual(query.count(), 1)
        result = query.one()
        self.assertEqual(len(result.mapped_system_ids()), 4)
        with self.assertRaises(ValueError) as context:
            result.remove_mapped_system(str(uuid.uuid4()))
            self.assertTrue("Failed to remove system id" in str(context.exception))

    def test_cascade_delete(self):
        self.populate_db_with_stuff()
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account1,
            SystemBaseline.org_id == org_id1,
            SystemBaseline.display_name == "baseline1",
        )
        self.assertEqual(query.count(), 1)
        result = query.one()
        db.session.delete(result)
        db.session.commit()

        query = SystemBaselineMappedSystem.query.filter(
            SystemBaselineMappedSystem.account == account1,
            SystemBaselineMappedSystem.org_id == org_id1,
            SystemBaselineMappedSystem.system_id == system_id2,
        )
        self.assertEqual(query.count(), 0)

    def test_retrieve_baselines_for_uuid_system_id(self):
        self.populate_db_with_stuff()
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account2,
            SystemBaseline.org_id == org_id2,
            SystemBaseline.mapped_systems.any(SystemBaselineMappedSystem.system_id == system_id6),
        )
        self.assertEqual(query.count(), 2)
        results = query.all()
        for system_baseline in results:
            self.assertIn(
                system_baseline.display_name,
                (
                    "baseline3",
                    "baseline4",
                ),
            )

    def test_retrieve_baselines_for_str_system_id(self):
        self.populate_db_with_stuff()
        query = SystemBaseline.query.filter(
            SystemBaseline.account == account2,
            SystemBaseline.org_id == org_id2,
            SystemBaseline.mapped_systems.any(
                SystemBaselineMappedSystem.system_id == str(system_id6)
            ),
        )
        self.assertEqual(query.count(), 2)
        results = query.all()
        for system_baseline in results:
            self.assertIn(
                system_baseline.display_name,
                (
                    "baseline3",
                    "baseline4",
                ),
            )

    def test_delete_systems_by_ids(self):
        self.populate_db_with_stuff()

        SystemBaselineMappedSystem.delete_by_system_ids(
            [system_id2, system_id5, system_id4],
            account1,
            org_id1,
        )

        systems = SystemBaselineMappedSystem.query.all()
        system_ids = [system.system_id for system in systems]

        self.assertIn(system_id1, system_ids)
        self.assertNotIn(system_id2, system_ids)
        self.assertIn(system_id3, system_ids)
        self.assertNotIn(system_id4, system_ids)
        self.assertNotIn(system_id5, system_ids)
        self.assertIn(system_id6, system_ids)
        self.assertIn(system_id7, system_ids)
        self.assertIn(system_id8, system_ids)
        self.assertIn(system_id9, system_ids)

    def test_get_mapped_system_count(self):
        self.populate_db_with_stuff()

        mapped_systems_count = SystemBaselineMappedSystem.get_mapped_system_count(account1, org_id1)

        self.assertEqual(
            sorted(mapped_systems_count), sorted([(baseline_id1, 3), (baseline_id2, 2)])
        )

        mapped_systems_count = SystemBaselineMappedSystem.get_mapped_system_count(account2, org_id2)

        self.assertEqual(
            sorted(mapped_systems_count), sorted([(baseline_id3, 2), (baseline_id4, 3)])
        )


class MappedSystemsWithGroupsTest(DbModelTest):
    def populate_db_with_stuff(self):
        # we care only about mapped systems with groups (or without) for these tests
        rows = [
            SystemBaseline(
                account=account1,
                org_id=org_id1,
                id=baseline_with_systems_with_groups,
                display_name="baseline_with_systems_with_groups",
                baseline_facts=baseline_facts,
                mapped_systems=[
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id1,
                        groups=[{"id": "group_id_1", "name": "group_name_1"}],
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id2,
                        groups=[{"id": "group_id_2", "name": "group_name_2"}],
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id3,
                        groups=[
                            {"id": "group_id_1", "name": "group_name_1"},
                            {"id": "group_id_3", "name": "group_name_3"},
                        ],
                    ),
                    SystemBaselineMappedSystem(
                        account=account1,
                        org_id=org_id1,
                        system_id=system_id4,
                        groups=[],
                    ),
                ],
            ),
        ]
        db.session.add_all(rows)
        db.session.commit()

    def test_get_mapped_system_ids(self):
        self.populate_db_with_stuff()

        baseline = SystemBaseline.query.filter(
            SystemBaseline.id == baseline_with_systems_with_groups,
        ).one()

        mapped_systems = baseline.mapped_system_ids()
        self.assertEqual(4, len(mapped_systems))

        rbac_group_filters = [{"id": "group_id_1"}]
        mapped_systems = baseline.mapped_system_ids(rbac_group_filters=rbac_group_filters)
        self.assertEqual(2, len(mapped_systems))

        rbac_group_filters = [{"id": "group_id_1"}, {"id": "group_id_2"}]
        mapped_systems = baseline.mapped_system_ids(rbac_group_filters=rbac_group_filters)
        self.assertEqual(3, len(mapped_systems))

        rbac_group_filters = [{"id": "group_id_3"}]
        mapped_systems = baseline.mapped_system_ids(rbac_group_filters=rbac_group_filters)
        self.assertEqual(1, len(mapped_systems))

        rbac_group_filters = [{"id": None}]
        mapped_systems = baseline.mapped_system_ids(rbac_group_filters=rbac_group_filters)
        self.assertEqual(1, len(mapped_systems))
