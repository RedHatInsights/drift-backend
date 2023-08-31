import base64
import json
import logging
import re

from http import HTTPStatus

from requests.exceptions import Timeout

from kerlescan.config import drift_shared_secret, enable_rbac, enable_smart_mgmt_check, path_prefix
from kerlescan.exceptions import HTTPError, RBACDenied
from kerlescan.rbac_service_interface import get_perms
from kerlescan.service_interface import get_key_from_headers


def get_account_number(request):
    """
    This is different than ensure_account_number. This will return the number
    whereas the other method raises an exception if the number does not exist
    on the request.
    """
    auth_key = get_key_from_headers(request.headers)
    identity = json.loads(base64.b64decode(auth_key))["identity"]
    return identity.get("account_number")


def get_org_id(request):
    """
    This is different than ensure_org_id. This will return the number
    whereas the other method raises an exception if the number does not exist
    on the request.
    """
    auth_key = get_key_from_headers(request.headers)
    identity = json.loads(base64.b64decode(auth_key))["identity"]
    return identity.get("org_id")


def _is_mgmt_url(path):
    """
    small helper to test if URL is for management API.
    """
    return path.startswith("/mgmt/")


def _is_openapi_url(path, app_name):
    """
    small helper to test if URL is the openapi spec
    """
    return path == "%s%s/v1/openapi.json" % (path_prefix, app_name)


def check_request_from_drift_service(**kwargs):
    """
    check_request_from_drift_service kwargs need to contain: request
    This method check if the request comes from our drift service.
    """
    request = kwargs["request"]
    logger = kwargs["logger"]
    auth_key = get_key_from_headers(request.headers)

    if auth_key is None:
        return False

    auth = json.loads(base64.b64decode(auth_key))
    identity_type = auth.get("identity", {}).get("type", None)
    if identity_type == "System":
        request_shared_secret = request.headers.get("x-rh-drift-internal-api", None)
        if request_shared_secret and request_shared_secret == drift_shared_secret:
            logger.audit("shared-secret found, auth/entitlement authorized")
            return True  # shared secret set and is correct

    return False


def check_request_from_turnpike(**kwargs):
    """
    check_request_from_turnpike kwargs need to contain: request
    This method check if the request comes from Turnpike
    """
    request = kwargs["request"]
    logger = kwargs["logger"]
    auth_key = get_key_from_headers(request.headers)

    if auth_key is None:
        return False

    auth = json.loads(base64.b64decode(auth_key))
    identity_type = auth.get("identity", {}).get("type", None)

    if identity_type == "Associate":
        logger.audit("Associate account/org found, auth/entitlement authorized")
        return True

    return False


def ensure_account_number(**kwargs):
    request = kwargs["request"]
    logger = kwargs["logger"]
    app_name = kwargs["app_name"]

    if (
        _is_mgmt_url(request.path)
        or check_request_from_turnpike(request=request, logger=logger)
        or _is_openapi_url(request.path, app_name)
    ):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        identity = json.loads(base64.b64decode(auth_key))["identity"]
        if "account_number" not in identity:
            logger.debug("account number not found on identity token %s" % auth_key)
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message="account number not found on identity token",
            )
    else:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="identity not found on request")


def ensure_org_id(**kwargs):
    request = kwargs["request"]
    logger = kwargs["logger"]
    app_name = kwargs["app_name"]

    if (
        _is_mgmt_url(request.path)
        or check_request_from_turnpike(request=request, logger=logger)
        or _is_openapi_url(request.path, app_name)
    ):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        identity = json.loads(base64.b64decode(auth_key))["identity"]
        if "org_id" not in identity:
            logger.debug("org id not found on identity token %s" % auth_key)
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                message="org id not found on identity token",
            )
    else:
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="identity not found on request")


def ensure_has_permission(**kwargs):
    """
    ensure permission exists. kwargs needs to contain:
        permissions, application, app_name, request, logger, request_metric, exception_metric
    """
    request = kwargs["request"]
    logger = kwargs["logger"]
    app_name = kwargs["app_name"]

    if not enable_rbac:
        return

    if _is_mgmt_url(request.path) or _is_openapi_url(request.path, app_name):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)

    # check if the request comes from our own drift service
    if check_request_from_drift_service(**kwargs) or check_request_from_turnpike(**kwargs):
        return

    if not auth_key:
        logger.debug("entitlement not found for account/org.")
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="identity not found on request")

    try:
        perms = get_perms(
            ",".join(
                [kwargs["application"], "inventory"]
            ),  # we need to query permissions for the inventory app
            auth_key,
            logger,
            kwargs["request_metric"],
            kwargs["exception_metric"],
            kwargs.get("rbac_filters"),
        )
        # kwargs["permissions"] is now a list of lists.
        # At least one of the lists must work ("or"), but all permissions in each
        # sublist must work in order for that list to "work" ("and").
        # For example:
        # permissions=[["drift:*:*"], ["drift:notifications:read", "drift:baselines:read"]]
        # If we just have *:*, it works, but if not, we need both notifications:read and
        # baselines:read in order to allow access.
        logger.audit("Validating RBAC permission")
        found_one = False
        for p in kwargs["permissions"]:
            all_match = True
            for one_of_required in p:
                if one_of_required not in perms:
                    all_match = False
            if all_match:
                found_one = True
        if found_one:
            return  # allow
        raise HTTPError(
            HTTPStatus.FORBIDDEN,
            message="user does not have access to %s" % kwargs["permissions"],
        )
    except RBACDenied:
        raise HTTPError(
            HTTPStatus.FORBIDDEN,
            message="request to retrieve permissions from RBAC was forbidden",
        )
    except Timeout:
        raise HTTPError(HTTPStatus.REQUEST_TIMEOUT, message="Request to RBAC timed out")


def ensure_entitled(**kwargs):
    """
    check if the request is entitled. We run this on all requests and bail out
    if the URL is whitelisted. Returning 'None' allows the request to go through.
    """
    request = kwargs["request"]
    logger = kwargs["logger"]
    app_name = kwargs["app_name"]

    entitlement_key = "insights"
    if enable_smart_mgmt_check:
        entitlement_key = "smart_management"

    # TODO: Blueprint.before_request was not working as expected, using
    # before_app_request and checking URL here instead.
    if _is_mgmt_url(request.path) or _is_openapi_url(request.path, app_name):
        return  # allow request

    # check if the request comes from our own drift service
    if check_request_from_drift_service(
        request=request, logger=logger
    ) or check_request_from_turnpike(request=request, logger=logger):
        return

    auth_key = get_key_from_headers(request.headers)

    if not auth_key:
        logger.debug("entitlement not found for account/org.")
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="identity not found on request")

    entitlements = json.loads(base64.b64decode(auth_key)).get("entitlements", {})
    if entitlement_key in entitlements:
        if entitlements[entitlement_key].get("is_entitled"):
            logger.debug("enabled entitlement found on header")
            return  # allow request

    raise HTTPError(HTTPStatus.BAD_REQUEST, message="Entitlement not found for account/org.")


def log_username(**kwargs):
    request = kwargs["request"]
    logger = kwargs["logger"]

    if logger.level == logging.DEBUG:
        auth_key = get_key_from_headers(request.headers)
        if auth_key:
            identity = json.loads(base64.b64decode(auth_key))["identity"]
            if identity["type"] == "Associate":
                username = identity["associate"]["email"]
            else:
                username = identity["user"]["username"]
            logger.debug("username/associate from identity header: %s" % username)
        else:
            logger.debug("identity header not sent for request")


def validate_uuids(system_ids):
    """
    helper method to test if a UUID is properly formatted. Will raise an
    exception if the format is wrong.
    """
    malformed_ids = []
    compiled_regex = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")
    for system_id in system_ids:
        if not compiled_regex.match(system_id.lower()):
            malformed_ids.append(system_id)

    if malformed_ids:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            message="malformed UUIDs requested (%s)" % ", ".join(malformed_ids),
        )
