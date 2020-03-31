import time

from historical_system_profiles import config, listener_logging
from historical_system_profiles.app import create_app
from historical_system_profiles import db_interface


def main():
    logger = listener_logging.initialize_logging()
    logger.error(
        "starting expired record cleaning loop, will remove records older than "
        "%s days every %s minutes"
        % (config.valid_profile_age_days, config.expired_cleaner_sleep_minutes)
    )
    app = create_app()
    expired_record_cleaning_loop(app.app, logger)


def expired_record_cleaning_loop(flask_app, logger):
    with flask_app.app_context():
        while True:
            try:
                deleted_count = db_interface.clean_expired_records(
                    config.valid_profile_age_days
                )
                logger.info("deleted %s expired records" % deleted_count)
            except Exception:
                logger.exception(
                    "An error occurred during expired record cleaning loop"
                )
            logger.info(
                "sleeping for %s minutes" % config.expired_cleaner_sleep_minutes
            )
            time.sleep(config.expired_cleaner_sleep_minutes * 60)


if __name__ == "__main__":
    main()
