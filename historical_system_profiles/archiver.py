from historical_system_profiles import db_interface
from historical_system_profiles import listener_metrics as metrics


def _record_recv_message(host, request_id, ptc):
    metrics.profile_messages_consumed.inc()
    ptc.emit_received_message(
        "received inventory update event",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _record_success_message(host, request_id, ptc):
    metrics.profile_messages_processed.inc()
    ptc.emit_success_message(
        "stored historical profile",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )


def _archive_profile(data, ptc, logger):
    """
    given an event, archive a profile and emit a success message
    """
    host = data.value["host"]
    request_id = data.value["platform_metadata"].get("request_id")
    _record_recv_message(host, request_id, ptc)

    profile = host["system_profile"]
    # fqdn is on the host but we need it in the profile as well
    profile["fqdn"] = host["fqdn"]
    db_interface.create_profile(
        inventory_id=host["id"], profile=profile, account_number=host["account"],
    )

    _record_success_message(host, request_id, ptc)
    logger.info("wrote inventory_id %s's profile to historical database" % host["id"])


def _emit_archiver_error(data, ptc, logger):
    """
    send an error message to payload tracker. This does not raise an
    exception.
    """
    metrics.profile_messages_errored.inc()
    host = data.value["host"]
    request_id = data.value["platform_metadata"].get("request_id")
    ptc.emit_error_message(
        "error when storing historical profile",
        request_id=request_id,
        account=host["account"],
        inventory_id=host["id"],
    )
    logger.exception("An error occurred during message processing")


def event_loop(flask_app, consumer, ptc, logger):
    with flask_app.app_context():
        while True:
            for data in consumer:
                try:
                    _archive_profile(data, ptc, logger)
                except Exception:
                    _emit_archiver_error(data, ptc, logger)
