from prometheus_client import Counter, Gauge, Histogram


api_exceptions = Counter("baseline_api_exceptions", "count of exceptions raised on public API")

baseline_create_requests = Histogram("baseline_create_requests", "baseline create request stats")

baseline_fetch_requests = Histogram("baseline_fetch_requests", "baseline fetch request stats")

baseline_fetch_all_requests = Histogram(
    "baseline_fetch_all_requests", "baseline fetch all request stats"
)

baseline_delete_requests = Histogram("baseline_delete_requests", "baseline delete request stats")

inventory_service_requests = Histogram(
    "baseline_inventory_service_requests", "inventory service call stats"
)

inventory_service_exceptions = Counter(
    "baseline_inventory_service_exceptions", "count of exceptions raised by inv service"
)

hsp_service_requests = Histogram("baseline_hsp_service_requests", "hsp service call stats")

hsp_service_exceptions = Counter(
    "baseline_hsp_service_exceptions", "count of exceptions raised by hsp service"
)

# kerlescan expects this to be Histogram
inventory_service_no_profile = Histogram(
    "baseline_inventory_service_no_profile",
    "count of systems fetched without a profile",
)

baseline_count = Gauge(
    "baseline_count", "count of total number of baselines", multiprocess_mode="max"
)

baseline_account_count = Gauge(
    "baseline_account_count",
    "count of total number of accounts with baselines",
    multiprocess_mode="max",
)

baseline_account_count_ones = Gauge(
    "baseline_account_count_ones",
    "number of accounts with zero to ten baselines",
    multiprocess_mode="max",
)

baseline_account_count_tens = Gauge(
    "baseline_account_count_tens",
    "number of accounts with ten to one hundred baselines",
    multiprocess_mode="max",
)

baseline_account_count_hundred_plus = Gauge(
    "baseline_account_count_hundred_plus",
    "number of accounts with over one hundred baselines",
    multiprocess_mode="max",
)

rbac_requests = Histogram("baseline_rbac_service_requests", "rbac service call stats")
rbac_exceptions = Counter("baseline_rbac_exceptions", "count of exceptions raised by rbac service")
