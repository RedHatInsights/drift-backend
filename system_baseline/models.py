import uuid

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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
    account = db.Column(db.String(10), nullable=False)
    org_id = db.Column(db.String(36))
    display_name = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    baseline_facts = db.Column(JSONB)
    mapped_systems = relationship(
        "SystemBaselineMappedSystem",
        cascade="all, delete, delete-orphan",
    )
    dirty_systems = db.Column(db.Boolean, default=False, nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def fact_count(self):
        return len(self.baseline_facts)

    @validates("baseline_facts")
    def validate_facts(self, key, value):
        validators.check_facts_length(value)
        validators.check_for_duplicate_names(value)
        return value

    def mapped_system_ids(self):
        mapped_system_ids = []
        for mapped_system in self.mapped_systems:
            mapped_system_ids.append(str(mapped_system.system_id))
        return mapped_system_ids

    def to_json(self, withhold_facts=False, withhold_system_ids=True, withhold_systems_count=True):
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account
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

    def add_mapped_system(self, system_id):
        self.validate_existing_system(system_id)
        new_mapped_system = SystemBaselineMappedSystem(
            system_id=system_id, account=self.account, org_id=self.org_id
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
    account = db.Column(db.String(10), nullable=False)
    org_id = db.Column(db.String(36))
    system_baseline_id = db.Column(
        UUID(as_uuid=True), ForeignKey("system_baselines.id"), nullable=False
    )
    system_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    @classmethod
    def delete_by_system_ids(cls, system_ids, account_number, org_id):
        if org_id:
            query = cls.query.filter(cls.system_id.in_(system_ids), cls.org_id == org_id)
        else:
            query = cls.query.filter(cls.system_id.in_(system_ids), cls.account == account_number)

        query.delete(synchronize_session="fetch")
        db.session.commit()

    @classmethod
    def get_mapped_system_count(cls, account_number, org_id):
        query = cls.query.with_entities(
            cls.system_baseline_id, func.count(cls.system_baseline_id)
        ).group_by(cls.system_baseline_id)

        if org_id:
            results = query.filter(cls.org_id == org_id).all()
        else:
            results = query.filter(cls.account == account_number).all()

        return results
