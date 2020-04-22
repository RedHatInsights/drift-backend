from historical_system_profiles import db_interface


def _archive_profile(data, ptc, logger):
    """
    given an event, archive a profile and emit a success message
    """
    host = data.value["host"]
    request_id = data.value["platform_metadata"].get("request_id")
    ptc.emit_received_message(
        "received inventory update event",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )
    profile = host["system_profile"]
    # fqdn is on the host but we need it in the profile as well
    profile["fqdn"] = host["fqdn"]
    db_interface.create_profile(
        inventory_id=host["id"], profile=profile, account_number=host["account"],
    )
    logger.info("wrote inventory_id %s's profile to historical database" % host["id"])
    ptc.emit_success_message(
        "stored historical profile",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _emit_archiver_error(data, ptc):
    """
    send an error message to payload tracker. This does not raise an
    exception.
    """
    host = data.value["host"]
    request_id = data.value["platform_metadata"].get("request_id")
    ptc.emit_error_message(
        "error when storing historical profile",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def event_loop(flask_app, consumer, ptc, logger):
    with flask_app.app_context():
        while True:
            for data in consumer:
                try:
                    _archive_profile(data, ptc, logger)
                except Exception:
                    host = data.value["host"]
                    request_id = data.value["platform_metadata"].get("request_id")
                    ptc.emit_error_message(
                        "error when storing historical profile",
                        request_id=request_id,
                        account=host["account"],
                        inventory_id=host["id"],
                    )
                    logger.exception("An error occurred during message processing")
