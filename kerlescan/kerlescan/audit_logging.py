import base64
import json
import logging

from kerlescan.service_interface import get_key_from_headers
from kerlescan.view_helpers import get_org_id


AUDIT_LEVEL_NAME = "AUDIT"
AUDIT_LEVEL_NUM = int((logging.INFO + logging.WARNING) / 2)


def audit(self, message, *args, **kws):
    """Sends a message to audit log

    :param message: message to be sent to audit log
    :type message: str
    :keyword request: flask request object; optional
    :type request: flask request object
    :keyword success: whether the action logged is success; optional
    :type success: bool
    :return: audit should return None
    :rtype: None
    """

    if self.isEnabledFor(AUDIT_LEVEL_NUM):
        request = kws.pop("request", None)
        success = kws.pop("success", None)
        audit_message = ""
        identificator = ""

        if request:
            auth_key = get_key_from_headers(request.headers)
            try:
                identificator = f"org id: {get_org_id(request)} - "
            except BaseException:
                pass

            if auth_key:
                identity = json.loads(base64.b64decode(auth_key)).get("identity", {})
                username = identity.get("user", {}).get("username", None)
                if username:
                    audit_message = f"user: {username} - "

        if success is not None:
            if success:
                audit_message = f"{audit_message}success - "
            else:
                audit_message = f"{audit_message}failure - "

        audit_message = audit_message + identificator + str(message)

        self._log(AUDIT_LEVEL_NUM, audit_message, args, **kws)


def setup_audit_logging(logger):
    logging.addLevelName(AUDIT_LEVEL_NUM, AUDIT_LEVEL_NAME)
    logging.Logger.audit = audit
