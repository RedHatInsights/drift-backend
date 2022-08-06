from datetime import datetime, timedelta

from flask import current_app, request
from sqlalchemy.exc import SQLAlchemyError

from historical_system_profiles.models import HistoricalSystemProfile, db


def rollback_on_exception(func):
    """
    any method that does a commit should have this decorator. It will roll back
    ORM transactions in the event of an exception.
    """

    def wrapper_rollback(*args, **kwargs):
        try:
            retval = func(*args, **kwargs)
            return retval
        except SQLAlchemyError as error:
            db.session.rollback()
            message = error.message
            current_app.logger.audit(message, request=request, success=False)
            raise

    return wrapper_rollback


@rollback_on_exception
def create_profile(inventory_id, profile, account_number, org_id):
    profile = HistoricalSystemProfile(
        account=account_number,
        org_id=org_id,
        inventory_id=inventory_id,
        system_profile=profile,
    )
    db.session.add(profile)
    db.session.commit()

    message = "created historical system profiles"
    current_app.logger.audit(message, request=request, success=True)

    return profile


def get_hsps_by_inventory_id(inventory_id, account_number, org_id, limit, offset):
    if account_number:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.account == account_number,
            HistoricalSystemProfile.inventory_id == inventory_id,
        )
    else:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.org_id == org_id,
            HistoricalSystemProfile.inventory_id == inventory_id,
        )

    query = query.order_by(HistoricalSystemProfile.captured_on.desc())
    query = query.limit(limit).offset(offset)
    query_results = query.all()

    message = "read historical system profiles"
    current_app.logger.audit(message, request=request, success=True)

    return query_results


def is_profile_recorded(captured_date, inventory_id, account_number, org_id):
    """
    returns True if an existing system profile exists with the same
    captured date + inventory id + account number or org_id.
    org_id is preferred to account_number.

    This could possibly be enforced in the DB schema. I'm doing it here for now
    so we have more flexbility if we want to change the rules on this later.
    """
    if account_number:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.account == account_number,
            HistoricalSystemProfile.inventory_id == inventory_id,
            HistoricalSystemProfile.captured_on == captured_date,
        )
    else:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.org_id == org_id,
            HistoricalSystemProfile.inventory_id == inventory_id,
            HistoricalSystemProfile.captured_on == captured_date,
        )

    message = "read historical system profiles"
    current_app.logger.audit(message, request=request)
    if query.first():
        return True
    return False


@rollback_on_exception
def delete_hsps_by_inventory_id(inventory_id):
    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.inventory_id == inventory_id,
    )
    query.delete(synchronize_session="fetch")
    db.session.commit()

    message = "deleted historical system profiles"
    current_app.logger.audit(message, request=request, success=True)


def get_hsps_by_profile_ids(profile_ids, account_number, org_id):
    if account_number:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.account == account_number,
            HistoricalSystemProfile.id.in_(profile_ids),
        )
    else:
        query = HistoricalSystemProfile.query.filter(
            HistoricalSystemProfile.org_id == org_id,
            HistoricalSystemProfile.id.in_(profile_ids),
        )

    query_results = query.all()

    message = "read historical system profiles"
    current_app.logger.audit(message, request=request, success=True)

    return query_results


@rollback_on_exception
def clean_expired_records(days_til_expired):
    now = datetime.now()
    expired_time = now - timedelta(days=days_til_expired)

    query = HistoricalSystemProfile.query.filter(HistoricalSystemProfile.created_on < expired_time)
    count = query.delete(synchronize_session="fetch")

    db.session.commit()

    message = "cleaned expired historical system profiles"
    current_app.logger.audit(message, request=request, success=True)

    return count
