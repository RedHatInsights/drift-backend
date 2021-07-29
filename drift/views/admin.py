from flask import Blueprint, jsonify

from drift.version import app_version


section = Blueprint("internal_admin", __name__)


@section.before_app_request
def status():
    return jsonify(
        {
            "drift_version": app_version,
            "status": "Warning! This is a test data.",
            "totalBaselinesCount": 541,
            "customerIdsCount": 279,
            "BaselinesBuckets": {"1": 206, "2": 46, "3": 11, "4": 4, "10+": 7, "5-10": 5},
            "createdBaselinesToday": 3,
            "createdBaselinesWeek": 11,
            "createdBaselinesMonth": 47,
            "totalBaselinesWithAssociationsCount": 25,
            "BaselinesAssociationsBuckets": {"1": 19, "2": 4, "3": 1, "4": 1, "10+": 0, "5-10": 0},
        }
    )
