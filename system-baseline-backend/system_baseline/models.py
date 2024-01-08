import uuid

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, func, or_, update
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.schema import ForeignKey, UniqueConstraint

from system_baseline import validators


db = SQLAlchemy()

FACTS_MAXSIZE = 2**19  # 512KB


class SystemBaseline(db.Model):
    __tablename__ = "system_baselines"
    # do not allow two records in the same account to have the same display name
    __table_args__ = (UniqueConstraint("account", "display_name", name="_account_display_name_uc"),)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10))
    org_id = db.Column(db.String(36), index=True)
    display_name = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    baseline_facts = db.Column(JSONB)
    mapped_systems = relationship(
        "SystemBaselineMappedSystem",
        cascade="all, delete, delete-orphan",
        lazy="dynamic",
    )
    dirty_systems = db.Column(db.Boolean, default=False, nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def fact_count(self):
        return len(self.baseline_facts)

    @validates("baseline_facts")
    def validate_facts(self, key, value):
        validators.check_facts_length(value)
        validators.check_for_duplicate_names(value)
        return value

    @staticmethod
    def get_groups_query_filters(filters):
        return [
            SystemBaselineMappedSystem.groups == "[]"
            if "id" in filter and filter["id"] is None
            else SystemBaselineMappedSystem.groups.contains(cast([filter], JSONB))
            for filter in filters
        ]

    def mapped_system_ids(self, rbac_group_filters=None, api_group_filters=None):
        # rbac_group_filters behaviour
        # format is a list of dictionaries
        # possible values:
        # None - no filter applied, all hosts allowed
        # [] - no groups ids present, no hosts allowed
        # [{}, {}] - group ids present, get values of "id" keys
        # or hosts with no group present (None value in "id" key)
        # [{'id': None}, {'id': '39eb2f52-37c1-4f75-95e6-7237d0b385b7'}]

        mapped_systems_query = self.mapped_systems

        if rbac_group_filters:
            mapped_systems_query = mapped_systems_query.filter(
                or_(*self.get_groups_query_filters(rbac_group_filters))
            )

        if api_group_filters:
            mapped_systems_query = mapped_systems_query.filter(
                or_(*self.get_groups_query_filters(api_group_filters))
            )

        mapped_system_ids = []
        for mapped_system in mapped_systems_query:
            mapped_system_ids.append(str(mapped_system.system_id))
        return mapped_system_ids

    def to_json(self, withhold_facts=False, withhold_system_ids=True, withhold_systems_count=True):
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account if self.account else ""
        json_dict["org_id"] = self.org_id
        json_dict["display_name"] = self.display_name
        json_dict["fact_count"] = self.fact_count
        json_dict["created"] = self.created_on.isoformat() + "Z"
        json_dict["updated"] = self.modified_on.isoformat() + "Z"
        json_dict["notifications_enabled"] = self.notifications_enabled
        if not withhold_facts:
            json_dict["baseline_facts"] = self.baseline_facts
        if not withhold_system_ids:
            json_dict["system_ids"] = self.mapped_system_ids()
        if not withhold_systems_count:
            json_dict["mapped_system_count"] = len(self.mapped_system_ids())
        return json_dict

    def validate_existing_system(self, system_id):
        for mapped_system in self.mapped_systems:
            if system_id == str(mapped_system.system_id):
                raise ValueError(
                    "System {} already associated with this baseline".format(system_id)
                )

    def add_mapped_system(self, system_id, groups=None):
        self.validate_existing_system(system_id)
        new_mapped_system = SystemBaselineMappedSystem(
            system_id=system_id, account=self.account, org_id=self.org_id, groups=groups
        )
        self.mapped_systems.append(new_mapped_system)
        db.session.add(new_mapped_system)

    def remove_mapped_system(self, system_id):
        system_id_removed = False
        for mapped_system in self.mapped_systems:
            if str(mapped_system.system_id) == str(system_id):
                self.mapped_systems.remove(mapped_system)
                system_id_removed = True
                break
        if not system_id_removed:
            # do we want to raise exception here?
            raise ValueError(
                "Failed to remove system id %s from mapped systems - not in list" % system_id
            )


class SystemBaselineMappedSystem(db.Model):
    __tablename__ = "system_baseline_mapped_systems"
    __table_args__ = (
        UniqueConstraint(
            "system_baseline_id", "system_id", name="_system_baseline_mapped_system_uc"
        ),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10))
    org_id = db.Column(db.String(36), index=True)
    system_baseline_id = db.Column(
        UUID(as_uuid=True), ForeignKey("system_baselines.id"), nullable=False
    )
    system_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    groups = db.Column(JSONB)

    def to_json(self):
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account if self.account else ""
        json_dict["org_id"] = self.org_id
        json_dict["system_baseline_id"] = self.system_baseline_id
        json_dict["groups"] = self.groups
        return json_dict

    @classmethod
    def delete_by_system_ids(cls, system_ids, account_number, org_id):
        if org_id:
            query = cls.query.filter(cls.system_id.in_(system_ids), cls.org_id == org_id)
        else:
            query = cls.query.filter(cls.system_id.in_(system_ids), cls.account == account_number)

        query.delete(synchronize_session="fetch")
        db.session.commit()

    @classmethod
    def get_mapped_system_count(cls, account_number, org_id, rbac_group_filters=None):
        mapped_systems_query = cls.query
        if rbac_group_filters is not None:
            mapped_systems_query = mapped_systems_query.filter(
                or_(*SystemBaseline.get_groups_query_filters(rbac_group_filters))
            )

        query = mapped_systems_query.with_entities(
            cls.system_baseline_id, func.count(cls.system_baseline_id)
        ).group_by(cls.system_baseline_id)

        if org_id:
            results = query.filter(cls.org_id == org_id).all()
        else:
            results = query.filter(cls.account == account_number).all()

        return results

    @classmethod
    def update_systems(cls, system_id, groups=None):
        if groups is None:
            return

        query = (
            update(cls)
            .where(cls.system_id == system_id)
            .values(groups=groups)
            .returning(cls.id, cls.system_id, cls.system_baseline_id, cls.groups)
        )
        updated_systems_data = db.session.execute(query).all()
        db.session.commit()
        return [
            cls(id=data[0], system_id=data[1], system_baseline_id=data[2], groups=data[3])
            for data in updated_systems_data
        ]
