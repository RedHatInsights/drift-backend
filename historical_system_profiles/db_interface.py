from datetime import datetime, timedelta
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError

from kerlescan.exceptions import HTTPError, ItemNotReturned
from kerlescan.inventory_service_interface import ensure_correct_system_count

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
        except SQLAlchemyError:
            db.session.rollback()
            raise

    return wrapper_rollback


@rollback_on_exception
def create_profile(inventory_id, profile, account_number):
    profile = HistoricalSystemProfile(
        account=account_number, inventory_id=inventory_id, system_profile=profile,
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def get_hsps_by_inventory_id(inventory_id, account_number):
    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.inventory_id == inventory_id,
    )

    query_results = query.all()

    if query_results:
        return query_results
    raise HTTPError(HTTPStatus.NOT_FOUND, message="%s not available" % inventory_id)


@rollback_on_exception
def delete_hsps_by_inventory_id(inventory_id):
    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.inventory_id == inventory_id,
    )
    query.delete(synchronize_session="fetch")
    db.session.commit()


def get_hsps_by_profile_ids(profile_ids, account_number):
    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.account == account_number,
        HistoricalSystemProfile.id.in_(profile_ids),
    )

    query_results = query.all()
    try:
        ensure_correct_system_count(profile_ids, query_results)
    except ItemNotReturned as e:
        raise HTTPError(HTTPStatus.NOT_FOUND, message=e.message)

    return query_results


@rollback_on_exception
def clean_expired_records(days_til_expired):
    now = datetime.now()
    expired_time = now - timedelta(days=days_til_expired)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.created_on < expired_time
    )
    count = query.delete(synchronize_session="fetch")
    db.session.commit()
    return count
