import json

from kafka import KafkaConsumer

from historical_system_profiles import config, listener_logging
from historical_system_profiles.app import create_app
from historical_system_profiles import archiver
from historical_system_profiles import deleter
from historical_system_profiles import payload_tracker_interface


def main():
    logger = listener_logging.initialize_logging()
    logger.error("starting %s listener" % config.listener_type)

    app = create_app()
    ptc = payload_tracker_interface.PayloadTrackerClient(logger)

    if config.listener_type == "ARCHIVER":
        consumer = init_consumer("platform.inventory.host-egress")
        archiver.event_loop(app.app, consumer, ptc, logger)
    elif config.listener_type == "DELETER":
        consumer = init_consumer("platform.inventory.events")
        deleter.event_loop(app.app, consumer, ptc, logger)
    else:
        logger.error("unable to detect listener type")


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
