from prometheus_client import Counter, Summary


profile_messages_consumed = Counter(
    "hsp_profile_messages_consumed", "count of profile messages we consumed"
)

profile_messages_processed = Counter(
    "hsp_profile_messages_processed",
    "count of profile messages we successfully processed",
)

profile_messages_processed_duplicates = Counter(
    "hsp_profile_messages_processed_duplicates",
    "count of profile messages that were already in the database",
)


profile_messages_errored = Counter(
    "hsp_profile_messages_errored",
    "count of profile messages we unsuccessfully processed",
)

delete_messages_consumed = Counter(
    "hsp_delete_messages_consumed", "count of delete messages we consumed"
)

delete_messages_processed = Counter(
    "hsp_delete_messages_processed",
    "count of delete messages we successfully processed",
)

delete_messages_errored = Counter(
    "hsp_delete_messages_errored",
    "count of delete messages we unsuccessfully processed",
)

records_cleaned = Counter("hsp_records_cleaned", "count of records removed by cleaner")

records_cleaning_time = Summary("hsp_records_cleaning_time", "time spent cleaning records")
