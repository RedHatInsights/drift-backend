import logging
import os
import sys

import watchtower

from boto3.session import Session
from logstash_formatter import LogstashFormatterV1

from historical_system_profiles import app_config, config


# borrowed from https://git.io/JvKsY


def config_cloudwatch(logger):
    CW_SESSION = Session(
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_region_name,
    )
    cw_handler = watchtower.CloudWatchLogHandler(
        boto3_session=CW_SESSION,
        log_group=config.log_group,
        stream_name=config.hostname,
        create_log_group=False,
    )
    cw_handler.setFormatter(LogstashFormatterV1())
    logger.addHandler(cw_handler)


def initialize_logging():
    kafkalogger = logging.getLogger("kafka")
    kafkalogger.addHandler(logging.StreamHandler(sys.stdout))
    kafkalogger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    if any("KUBERNETES" in k for k in os.environ):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LogstashFormatterV1())
        logging.root.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        logging.root.addHandler(handler)
    else:
        logging.basicConfig(
            level="INFO", format="%(threadName)s %(levelname)s %(name)s - %(message)s"
        )

    logger = logging.getLogger(app_config.get_app_name())

    if config.aws_access_key_id and config.aws_secret_access_key:
        logger.warn("configuring cloudwatch logging")
        config_cloudwatch(logger)
        logger.warn("cloudwatch logging ENABLED")
    else:
        logger.warn("cloudwatch logging DISABLED")

    return logger
