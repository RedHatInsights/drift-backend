from datetime import datetime, timedelta
from historical_system_profiles.models import HistoricalSystemProfile, db


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
    return query_results


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
    return query_results


def clean_expired_records(days_til_expired):
    now = datetime.now()
    expired_time = now - timedelta(days=days_til_expired)

    query = HistoricalSystemProfile.query.filter(
        HistoricalSystemProfile.created_on < expired_time
    )
    count = query.delete(synchronize_session="fetch")
    db.session.commit()
    return count
