import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID

db = SQLAlchemy()


class HistoricalSystemProfile(db.Model):
    __tablename__ = "historical_system_profiles"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10))
    inventory_id = db.Column(UUID(as_uuid=True))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_on = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    system_profile = db.Column(JSONB)

    def __init__(self, system_profile, inventory_id, account):
        self.inventory_id = inventory_id
        self.account = account
        self.system_profile = system_profile
        # set the ID here so we can override the system profile's id with the historical profile
        generated_id = str(uuid.uuid4())
        self.id = generated_id
        self.system_profile["id"] = generated_id

    @property
    def display_name(self):
        return self.system_profile["display_name"]

    def to_json(self):
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account
        json_dict["inventory_id"] = self.inventory_id
        json_dict["created"] = self.created_on.isoformat() + "Z"
        json_dict["updated"] = self.modified_on.isoformat() + "Z"
        json_dict["system_profile"] = self.system_profile
        json_dict["display_name"] = self.display_name
        return json_dict
