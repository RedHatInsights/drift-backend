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


def get_hsps_by_ids(profile_ids):
    """
    return a list of historical system profiles for the given profile IDs
    """
    account_number = view_helpers.get_account_number(request)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.id.in_(profile_ids),
    )
    query_results = query.all()

    result = []
    for query_result in query_results:
        historical_sys_profile = query_result
        historical_sys_profile.system_profile["id"] = historical_sys_profile.id
        result.append(historical_sys_profile.to_json())

    return {"data": result}


def get_hsps_by_inventory_id(inventory_id):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.inventory_id == inventory_id,
    )

    query_results = query.all()
    if len(query_results) == 0:
        return {"data": []}
    else:
        result = {
            "inventory_uuid": inventory_id,
            "display_name": query_results[0].system_profile[
                "display_name"
            ],  # TODO: pull this from inventory instead of from the first record
        }
        profiles = [{"created": p.created_on, "id": p.id} for p in query_results]
        result["profiles"] = profiles
        return {"data": [result]}


def create_profile(body):
    """
    return a list of historical system profiles for a given inventory id
    """
    account_number = view_helpers.get_account_number(request)

    profile = HistoricalSystemProfile(
        account=account_number,
        inventory_id=body["inventory_id"],
        system_profile=body["profile"],
    )
    db.session.add(profile)
    db.session.commit()  # commit now so we get a created/updated time before json conversion

    return profile.to_json()
