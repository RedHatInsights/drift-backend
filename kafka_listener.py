import json

from kafka import KafkaConsumer

from historical_system_profiles import config, listener_logging
from historical_system_profiles.app import create_app
from historical_system_profiles import db_interface


def main():
    logger = listener_logging.initialize_logging()
    logger.error("starting %s listener" % config.listener_type)

    app = create_app()

    if config.listener_type == "ARCHIVER":
        archiver_event_loop(app.app, logger)
    elif config.listener_type == "DELETER":
        deleter_event_loop(app.app, logger)
    else:
        logger.error("unable to detect listener type")


def archiver_event_loop(flask_app, logger):
    consumer = init_consumer("platform.inventory.host-egress")
    with flask_app.app_context():
        while True:
            for data in consumer:
                try:
                    host = data.value["host"]
                    profile = host["system_profile"]
                    # fqdn is on the host but we need it in the profile as well
                    profile["fqdn"] = host["fqdn"]
                    db_interface.create_profile(
                        inventory_id=host["id"],
                        profile=profile,
                        account_number=host["account"],
                    )
                    logger.info(
                        "wrote inventory_id %s's profile to historical database"
                        % host["id"]
                    )
                except Exception:
                    logger.exception("An error occurred during message processing")


def deleter_event_loop(flask_app, logger):
    consumer = init_consumer("platform.inventory.events")
    with flask_app.app_context():
        while True:
            for data in consumer:
                try:
                    if data.value["type"] == "delete":
                        inventory_id = data.value["id"]
                        db_interface.delete_hsps_by_inventory_id(inventory_id)
                        logger.info(
                            "deleted profiles for inventory_id %s" % inventory_id
                        )
                except Exception:
                    logger.exception("An error occurred during message processing")


def init_consumer(queue):
    consumer = KafkaConsumer(
        queue,
        bootstrap_servers=config.bootstrap_servers,
        group_id=config.group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        retry_backoff_ms=1000,
        consumer_timeout_ms=200,
    )
    return consumer


if __name__ == "__main__":
    main()
