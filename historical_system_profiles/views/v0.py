from flask import Blueprint

section = Blueprint("v0", __name__)


def get_version():
    """
    return the service version
    """
    return {"version": "0.0.1"}


def get_historical_system_profiles():
    """
    return a list of historical system profiles
    """

    return {"100": "blah"}
