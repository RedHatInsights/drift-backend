import os

from app_common_python import LoadedConfig
from UnleashClient import UnleashClient


def initUnleash():
    configs = dict(
        UNLEASH_URL=os.getenv("UNLEASH_URL"),
        UNLEASH_TOKEN=os.getenv("UNLEASH_TOKEN"),
        UNLEASH_CACHE_DIR=os.getenv("UNLEASH_CACHE_DIR"),
    )
    UNLEASH_URL = "http://unleash_svc_url_is_not_set"
    UNLEASH_TOKEN = None
    unleash = LoadedConfig.featureFlags
    if unleash:
        UNLEASH_URL = f"{unleash.hostname}:{unleash.port}/api"
        if unleash.port == 443:
            UNLEASH_URL = f"https://{UNLEASH_URL}"
            UNLEASH_TOKEN = unleash.clientAccessToken
        else:
            UNLEASH_URL = f"http://{UNLEASH_URL}"
            UNLEASH_TOKEN = unleash.clientAccessToken

    configs["UNLEASH_URL"] = configs["UNLEASH_URL"] or UNLEASH_URL
    configs["UNLEASH_TOKEN"] = configs["UNLEASH_TOKEN"] or UNLEASH_TOKEN

    client = UnleashClient(
        url=configs["UNLEASH_URL"],
        app_name="drift",
        cache_directory=configs["UNLEASH_CACHE_DIR"],
        custom_headers={"Authorization": f'Bearer {configs["UNLEASH_TOKEN"]}'},
    )
    client.initialize_client()
    return client


UNLEASH = initUnleash()
