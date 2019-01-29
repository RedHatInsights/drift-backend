from flask import Blueprint, current_app, jsonify, request
import os
import requests
from requests import RequestException

from drift.views.phony_data import PHONY_DATA

# TODO: manage these settings in a config.py
APP_URL_PREFIX = "/r/insights/platform/drift"
API_VERSION_PREFIX = "/v0"
INVENTORY_SVC_URL = os.getenv('INVENTORY_SVC_URL', "http://inventory_svc_url_is_not_set")
INVENTORY_SVC_PATH = '/r/insights/platform/inventory/api/v1'

section = Blueprint('v0', __name__, url_prefix=APP_URL_PREFIX + API_VERSION_PREFIX)


@section.route("/compare")
def compare():
    if 'X-RH-IDENTITY' in request.headers:
        current_app.logger.debug("X-RH-IDENTITY received")
    return jsonify(PHONY_DATA)


@section.route("/status")
def status():
    inventory_connection_status = "fail"
    try:
        r = requests.get(INVENTORY_SVC_URL + INVENTORY_SVC_PATH + '/health')
        if r.status_code == requests.codes.ok:
            inventory_connection_status = "pass"
    except RequestException as re:
        current_app.logger.warn("Unable to contact inventory service: %s" % re)
        pass

    return jsonify({'status': "running", 'inventory_connection': inventory_connection_status})
