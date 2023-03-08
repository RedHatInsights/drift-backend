import os

import boto3
import watchtower

from app_common_python import LoadedConfig, isClowderEnabled


def setup_cw_logging(logger):  # pragma: no cover
    """
    initialize cloudwatch logging

    from https://github.com/RedHatInsights/cloudwatch-test
    """

    if isClowderEnabled():
        cloudwatch_cfg = LoadedConfig.logging.cloudwatch

        key_id = cloudwatch_cfg.accessKeyId
        secret = cloudwatch_cfg.secretAccessKey
        region = cloudwatch_cfg.region
        log_group = cloudwatch_cfg.logGroup

    else:
        key_id = os.environ.get("CW_AWS_ACCESS_KEY_ID")
        secret = os.environ.get("CW_AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_REGION", "us-east-1")
        log_group = os.environ.get("CW_LOG_GROUP", "platform-dev")

    if not (key_id and secret):
        logger.info("CloudWatch logging disabled due to missing access key")
        return

    boto3_logs_client = boto3.client(
        "logs", aws_access_key_id=key_id, aws_secret_access_key=secret, region_name=region
    )

    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read()
    except Exception:
        namespace = "unknown"

    handler = watchtower.CloudWatchLogHandler(
        boto3_client=boto3_logs_client,
        log_group_name=log_group,
        stream_name=namespace,
        create_log_group=False,
    )

    logger.addHandler(handler)
    logger.info("CloudWatch logging ENABLED!")
