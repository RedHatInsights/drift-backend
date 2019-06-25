AUTH_HEADER_NAME = "X-RH-IDENTITY"
FACT_NAMESPACE = "system_profile"
INVENTORY_SVC_SYSTEMS_ENDPOINT = "/api/inventory/v1/hosts/%s"
INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT = "/api/inventory/v1/hosts/%s/system_profile"
BASELINE_SVC_ENDPOINT = "/api/system-baseline/v0/baselines/%s"
SYSTEM_ID_KEY = "id"

COMPARISON_SAME = "SAME"
COMPARISON_DIFFERENT = "DIFFERENT"
COMPARISON_INCOMPLETE_DATA = "INCOMPLETE_DATA"

SYSTEM_PROFILE_BOOLEANS = {"satellite_managed"}
SYSTEM_PROFILE_INTEGERS = {"number_of_cpus", "number_of_sockets", "cores_per_socket"}
SYSTEM_PROFILE_STRINGS = {
    "infrastructure_type",
    "infrastructure_vendor",
    "bios_vendor",
    "bios_version",
    "bios_release_date",
    "os_release",
    "os_kernel_version",
    "arch",
    "last_boot_time",
    "cloud_provider",
    "fqdn",
}
SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED = {
    "cpu_flags",
    "kernel_modules",
    "enabled_services",
}
SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED = {"installed_services"}
