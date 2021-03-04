import logging
import json
import base64

from kerlescan.service_interface import get_key_from_headers

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

        if request:
            auth_key = get_key_from_headers(request.headers)
            identity = json.loads(base64.b64decode(auth_key)).get("identity", {})
            username = identity.get("user", {}).get("username", None)
            if username:
                audit_message = "user: " + username + " - "

        if success is not None:
            if success:
                audit_message = audit_message + "success" + " - "
            else:
                audit_message = audit_message + "failure" + " - "

        audit_message = audit_message + str(message)

        self._log(AUDIT_LEVEL_NUM, audit_message, args, **kws)


def setup_audit_logging(logger):
    logging.addLevelName(AUDIT_LEVEL_NUM, AUDIT_LEVEL_NAME)
    logging.Logger.audit = audit
