import os

from app_common_python import LoadedConfig
from UnleashClient import UnleashClient


def initUnleash():

    configs = dict(
        UNLEASH_URL=os.getenv("UNLEASH_URL"),
        UNLEASH_TOKEN=os.getenv("UNLEASH_TOKEN"),
    )
    unleash = LoadedConfig.featureFlags
    if unleash:
        UNLEASH_URL = f"{unleash.hostname}:{unleash.port}/api"
        if unleash.port == 443:
            UNLEASH_URL = f"https://{UNLEASH_URL}"
        else:
            UNLEASH_URL = f"http://{UNLEASH_URL}"

    configs["UNLEASH_URL"] = configs["UNLEASH_URL"] or UNLEASH_URL
    configs["UNLEASH_TOKEN"] = configs["UNLEASH_TOKEN"] or unleash.clientAccessToken

    client = UnleashClient(
        url=configs["UNLEASH_URL"],
        app_name="drift",
        custom_headers={"Authorization": configs["UNLEASH_TOKEN"]},
    )
    client.initialize_client()
    return client


UNLEASH = initUnleash()
