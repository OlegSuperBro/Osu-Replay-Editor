import requests

from config import CONSTANTS


def app_get_version():
    return requests.get("https://api.github.com/repos/OlegSuperBro/Osu-Replay-Editor/releases/latest").json()["name"]


def app_parse_version(version: str):
    return int("".join(version[1:].split("-")[0].split(".")))


def app_check_version(old_version, new_version):
    # True if update is avalable
    return app_parse_version(old_version) < app_parse_version(new_version)


def app_check_update():
    old_version = CONSTANTS.APP_VERSION
    new_version = app_get_version()
    return app_check_version(old_version, new_version)
