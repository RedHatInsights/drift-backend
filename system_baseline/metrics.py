from prometheus_client import Counter

api_exceptions = Counter(
    "system_baseline_api_exceptions", "count of exceptions raised on public API"
)
