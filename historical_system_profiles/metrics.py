from prometheus_client import Counter, Histogram

rbac_requests = Histogram("hsp_rbac_service_requests", "rbac service call stats")
rbac_exceptions = Counter(
    "hsp_rbac_exceptions", "count of exceptions raised by rbac service"
)
inventory_requests = Histogram(
    "hsp_inventory_service_requests", "inventory service call stats"
)
inventory_exceptions = Counter(
    "hsp_inventory_exceptions", "count of exceptions raised by inventory service"
)

# this metric is not relevant but kerlescan expects it
inventory_no_sysprofile = Histogram(
    "drift_systems_compared_no_sysprofile_UNUSED", "unused metric - do not use",
)
