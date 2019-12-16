from flask import Blueprint

from historical_system_profiles.mock_data import mocks

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
    if profile_ids == ["100"]:
        return mocks.MOCK_PROFILE_RESPONSE
    else:
        return {"results": []}


def get_pits_by_inventory_id(inventory_ids):
    """
    return a list of historical system profiles for a given inventory id
    """
    return mocks.MOCK_INV_RESPONSE
