import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID

db = SQLAlchemy()


class SystemBaseline(db.Model):
    __tablename__ = "system_baselines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10))
    display_name = db.Column(db.String(200))
    fact_count = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    baseline_facts = db.Column(JSONB)

    def __init__(self, baseline_facts, display_name=display_name, account=account):
        self.baseline_facts = baseline_facts
        self.display_name = display_name
        self.account = account
        self.fact_count = len(self.baseline_facts)

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
