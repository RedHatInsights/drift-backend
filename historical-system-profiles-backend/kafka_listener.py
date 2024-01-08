import json

from kafka import KafkaConsumer
from prometheus_client import start_http_server as start_metrics_server

from historical_system_profiles import (
    archiver,
    config,
    deleter,
    listener_logging,
    payload_tracker_interface,
)
from historical_system_profiles.app import create_app


def main():
    logger = listener_logging.initialize_logging()
    logger.error("starting %s listener" % config.listener_type)

    start_metrics_server(config.listener_metrics_port)

    app = create_app()
    ptc = payload_tracker_interface.PayloadTrackerClient(logger)

    consumer = init_consumer(config.consume_topic, logger)

    if config.listener_type == "ARCHIVER":
        archiver.event_loop(app.app, consumer, ptc, logger, config.listener_delay)
    elif config.listener_type == "DELETER":
        deleter.event_loop(app.app, consumer, ptc, logger, config.listener_delay)
    else:
        logger.error("unable to detect listener type")


def init_consumer(queue, logger):
    logger.info(
        f"creating {'secure' if config.enable_kafka_ssl else 'normal'} consumer "
        f"of {queue} with kafka_group_id {config.kafka_group_id}"
    )
    logger.info(f"kafka max poll interval (msec): {config.kafka_max_poll_interval_ms}")
    logger.info(f"kafka max poll records: {config.kafka_max_poll_records}")
    if config.enable_kafka_ssl:
        logger.info("Creating Consumer with SSL")
        consumer = KafkaConsumer(
            queue,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.kafka_group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            retry_backoff_ms=1000,
            consumer_timeout_ms=1000,
            api_version=(0, 10, 1),
            max_poll_interval_ms=config.kafka_max_poll_interval_ms,
            max_poll_records=config.kafka_max_poll_records,
            security_protocol=config.kafka_security_protocol,
            sasl_mechanism=config.kafka_sasl_mechanism,
            ssl_cafile=config.kafka_ssl_cert,
            sasl_plain_username=config.kafka_sasl_username,
            sasl_plain_password=config.kafka_sasl_password,
        )
    else:
        consumer = KafkaConsumer(
            queue,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.kafka_group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            retry_backoff_ms=1000,
            consumer_timeout_ms=1000,
            api_version=(0, 10, 1),
            max_poll_interval_ms=config.kafka_max_poll_interval_ms,
            max_poll_records=config.kafka_max_poll_records,
        )
    return consumer


if __name__ == "__main__":
    main()
