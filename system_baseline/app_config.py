import os


def get_app_name():
    """
    small helper to get application name
    """
    return os.getenv("APP_NAME", "system-baseline")
