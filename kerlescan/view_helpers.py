import json
import logging
import base64

from http import HTTPStatus

from kerlescan.config import path_prefix, enable_rbac
from kerlescan.service_interface import get_key_from_headers
from kerlescan.rbac_service_interface import get_roles
from kerlescan.exceptions import HTTPError


def get_account_number(request):
    """
    This is different than ensure_account_number. This will return the number
    whereas the other method raises an exception if the number does not exist
    on the request.
    """
    auth_key = get_key_from_headers(request.headers)
    identity = json.loads(base64.b64decode(auth_key))["identity"]
    return identity["account_number"]


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


def ensure_account_number(request, logger):
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


def ensure_has_role(**kwargs):
    """
    ensure role exists. kwargs needs to contain:
        role, application, app_name, request, logger, request_metric, exception_metric
    """
    if not enable_rbac:
        return

    request = kwargs["request"]
    if _is_mgmt_url(request.path) or _is_openapi_url(request.path, kwargs["app_name"]):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        roles = get_roles(
            kwargs["application"],
            auth_key,
            kwargs["logger"],
            kwargs["request_metric"],
            kwargs["exception_metric"],
        )
        if kwargs["role"] in roles:
            return  # allow
        else:
            raise HTTPError(
                HTTPStatus.FORBIDDEN,
                message="user does not have access to %s" % kwargs["role"],
            )
    else:
        # if we got here, reject the request
        raise HTTPError(HTTPStatus.BAD_REQUEST, message="identity not found on request")


def ensure_entitled(request, app_name, logger):
    """
    check if the request is entitled. We run this on all requests and bail out
    if the URL is whitelisted. Returning 'None' allows the request to go through.
    """
    # TODO: Blueprint.before_request was not working as expected, using
    # before_app_request and checking URL here instead.
    if _is_mgmt_url(request.path) or _is_openapi_url(request.path, app_name):
        return  # allow request

    auth_key = get_key_from_headers(request.headers)
    if auth_key:
        entitlements = json.loads(base64.b64decode(auth_key)).get("entitlements", {})
        if "smart_management" in entitlements:
            if entitlements["smart_management"].get("is_entitled"):
                logger.debug("enabled smart management entitlement found on header")
                return  # allow request
    else:
        logger.debug("identity header not sent for request")

    # if we got here, reject the request
    logger.debug("smart management entitlement not found for account.")
    raise HTTPError(
        HTTPStatus.BAD_REQUEST,
        message="Smart management entitlement not found for account.",
    )


def log_username(logger, request):
    if logger.level == logging.DEBUG:
        auth_key = get_key_from_headers(request.headers)
        if auth_key:
            identity = json.loads(base64.b64decode(auth_key))["identity"]
            logger.debug(
                "username from identity header: %s" % identity["user"]["username"]
            )
        else:
            logger.debug("identity header not sent for request")
