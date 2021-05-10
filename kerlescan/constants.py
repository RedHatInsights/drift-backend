AUTH_HEADER_NAME = "X-RH-IDENTITY"
VALID_HTTP_VERBS = ["get", "options", "head", "post", "put", "patch", "delete"]
FACT_NAMESPACE = "system_profile"
INVENTORY_SVC_SYSTEMS_ENDPOINT = "/api/inventory/v1/hosts/%s"
INVENTORY_SVC_SYSTEM_PROFILES_ENDPOINT = "/api/inventory/v1/hosts/%s/system_profile"
INVENTORY_SVC_SYSTEM_TAGS_ENDPOINT = "/api/inventory/v1/hosts/%s/tags"
BASELINE_SVC_ENDPOINT = "/api/system-baseline/v1/baselines/%s"
RBAC_SVC_ENDPOINT = "/api/rbac/v1/access/?application=%s"
HSP_SVC_ENDPOINT = "/api/historical-system-profiles/v1/profiles/%s"
DRIFT_SVC_ENDPOINT = "/api/drift/v1/comparison_report"
DRIFT_SVC_BASELINE_COMPARE_ENDPOINT = (
    DRIFT_SVC_ENDPOINT + "?system_ids[]=%s&baseline_ids[]=%s&short_circuit=True"
)
INTERNAL_BASELINE_SVC_ENDPOINT = (
    "/api/system-baseline/internal/v1/baselines?system_id=%s"
)  # note missing trailing slash
SYSTEM_ID_KEY = "id"

COMPARISON_SAME = "SAME"
COMPARISON_DIFFERENT = "DIFFERENT"
COMPARISON_INCOMPLETE_DATA = "INCOMPLETE_DATA"
COMPARISON_INCOMPLETE_DATA_OBFUSCATED = "INCOMPLETE_DATA_OBFUSCATED"

OBFUSCATED_FACTS_PATTERNS = {
    # enhanced matching for multiple IPs value
    "ipv4_addresses": r"^.*(10\.230\.230\.\d{1,3}){1}.*$",
    # hostname matching
    "fqdn": r"^host.*",
}

SYSTEM_PROFILE_BOOLEANS = {"sap_system", "satellite_managed"}
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
    "tuned_profile",
    "sap_instance_number",
    "sap_version",
    "selinux_current_mode",
    "selinux_config_file",
    "cpu_model",
}
SYSTEM_PROFILE_LISTS_OF_STRINGS_ENABLED = {
    "cpu_flags",
    "kernel_modules",
    "enabled_services",
}
SYSTEM_PROFILE_LISTS_OF_STRINGS_INSTALLED = {"installed_services"}
SYSTEM_PROFILE_LISTS_OF_STRINGS = {"gpg_pubkeys"}
GPG_KEY_PREFIX = "gpg-pubkey-"
SAP_RELATED_FACTS = {"sap_system", "sap_sids", "sap_instance_number", "sap_version"}
