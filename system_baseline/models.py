import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import validates

from system_baseline import validators

db = SQLAlchemy()

FACTS_MAXSIZE = 2 ** 19  # 512KB


class SystemBaseline(db.Model):
    __tablename__ = "system_baselines"
    # do not allow two records in the same account to have the same display name
    __table_args__ = (
        UniqueConstraint("account", "display_name", name="_account_display_name_uc"),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10), nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    baseline_facts = db.Column(JSONB)

    @property
    def fact_count(self):
        return len(self.baseline_facts)

    @validates("baseline_facts")
    def validate_facts(self, key, value):
        validators.check_facts_length(value)
        validators.check_for_duplicate_names(value)
        return value

    def __init__(self, baseline_facts, display_name=display_name, account=account):
        self.baseline_facts = baseline_facts
        self.display_name = display_name
        self.account = account

    def to_json(self, withhold_facts=False):
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account
        json_dict["display_name"] = self.display_name
        json_dict["fact_count"] = self.fact_count
        json_dict["created"] = self.created_on.isoformat() + "Z"
        json_dict["updated"] = self.modified_on.isoformat() + "Z"
        if not withhold_facts:
            json_dict["baseline_facts"] = self.baseline_facts
        return json_dict
