import base64
import json

from http import HTTPStatus

from flask import Blueprint, current_app, request
from kerlescan.exceptions import HTTPError
from kerlescan.service_interface import get_key_from_headers

from drift.baseline_service_interface import call_baseline_admin_svc


section = Blueprint("internal_admin", __name__)


def _check_turnpike_headers(**kwargs):
    auth_key = get_key_from_headers(request.headers)

    auth = json.loads(base64.b64decode(auth_key))
    identity_type = auth.get("identity", {}).get("type", None)

    return identity_type == "Associate"


def status():
    if _check_turnpike_headers(request=request):
        auth_key = get_key_from_headers(request.headers)
        result = call_baseline_admin_svc(
            endpoint="status", service_auth_key=auth_key, logger=current_app.logger
        )
        return result

    raise HTTPError(HTTPStatus.FORBIDDEN, message="Access Denied.")
