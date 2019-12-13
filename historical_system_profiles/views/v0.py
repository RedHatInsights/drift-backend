from flask import Blueprint

from historical_system_profiles.mock_data import mocks

section = Blueprint("v0", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "0.0.1"}


def get_pits_by_inventory_id(inventory_ids):
    """
    return a list of historical system profiles for a given inventory id
    """
    return mocks.MOCK_INV_RESPONSE
