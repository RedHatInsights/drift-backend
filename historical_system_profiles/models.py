import uuid

from datetime import datetime

import dateutil
import pytz

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID


db = SQLAlchemy()


class HistoricalSystemProfile(db.Model):
    __tablename__ = "historical_system_profiles"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account = db.Column(db.String(10), nullable=False)
    inventory_id = db.Column(UUID(as_uuid=True), index=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    system_profile = db.Column(JSONB)
    captured_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, system_profile, inventory_id, account):
        self.inventory_id = inventory_id
        self.account = account
        self.system_profile = system_profile
        # set the ID here so we can override the system profile's id with the historical profile
        generated_id = str(uuid.uuid4())
        self.id = generated_id
        self.system_profile["id"] = generated_id
        # set this now and not at commit time. It is needed as the fallback value for captured_on.
        self.created_on = datetime.utcnow()
        self.captured_on = self._get_captured_date()

    def _get_captured_date(self):
        captured_dt = self.created_on
        if self.system_profile.get("captured_date", None):
            captured_dt = dateutil.parser.parse(self.system_profile["captured_date"])

        return self._get_utc_aware_dt(captured_dt)

    def _get_utc_aware_dt(self, datetime_in):
        """
        https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive

        assume UTC if no timezone exists for captured_date. This field is read from
        `date --utc` on the client system; some records are in UTC but don't have a
        TZ due to a bug I introduced that's since been fixed.

        """
        if datetime_in.tzinfo is None or datetime_in.tzinfo.utcoffset(datetime_in) is None:
            return pytz.utc.localize(datetime_in)
        else:
            return datetime_in

    @property
    def display_name(self):
        return self.system_profile["display_name"]

    @property
    def captured_date(self):
        captured_dt = self.created_on
        if self.system_profile.get("captured_date", None):
            captured_dt = dateutil.parser.parse(self.system_profile["captured_date"])

        return self._get_utc_aware_dt(captured_dt)

    def to_json(self):
        created_dt = self._get_utc_aware_dt(self.created_on)
        json_dict = {}
        json_dict["id"] = str(self.id)
        json_dict["account"] = self.account
        json_dict["inventory_id"] = self.inventory_id
        json_dict["created"] = created_dt.isoformat()
        json_dict["system_profile"] = self.system_profile
        json_dict["display_name"] = self.display_name
        json_dict["captured_date"] = self.captured_date
        return json_dict
