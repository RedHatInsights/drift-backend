from flask import Blueprint, request
import json

from kerlescan import view_helpers

from historical_system_profiles.models import HistoricalSystemProfile, db


section = Blueprint("v0", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "0.0.1"}


def get_pits_by_ids(profile_ids):
    """
    return a list of historical system profiles for the given profile IDs
    """
    account_number = view_helpers.get_account_number(request)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.id.in_(profile_ids),
    )

    query_results = query.all()

    result = query_results[0]
    result.system_profile["id"] = profile_ids[0]
    result.id = profile_ids[0]

    return {"data": [result.to_json()]}


def get_pits_by_inventory_id(inventory_ids):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.inventory_id.in_(inventory_ids),
    )

    query_results = query.all()
    results = {
        "inventory_uuid": inventory_ids[0],
        "display_name": query_results[0].system_profile["display_name"],
    }

    profiles = [{"created": p.created_on, "id": p.id} for p in query_results]
    results["profiles"] = profiles

    return {"data": [results]}


def create_profile(body):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)

    # TODO no idea why this is needed..
    profile_in = json.loads(request.data.decode("utf-8"))

    profile = HistoricalSystemProfile(
        account=account_number,
        inventory_id=profile_in["inventory_id"],
        system_profile=profile_in["profile"],
    )
    db.session.add(profile)
    db.session.commit()  # commit now so we get a created/updated time before json conversion

    return profile.to_json()
