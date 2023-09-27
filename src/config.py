import yaml
import sys
import logging
from os.path import abspath, dirname, exists, isdir
from typing import List


class Config:
    app_ignore_updates: bool = False

    osu_path: str = "C:\\Games\\osu!"
    skin: str = "Default"

    enabled_plugins: List[str] = []

    def from_dict(self, env: dict):
        for key, value in env.items():
            if value is None:
                logging.warn(f"Value {key} is None, using default value {getattr(self, key)}")
                continue

            setattr(self, key, value)


class CONSTANTS:
    APP_VERSION = "v2023.9.26.0-alpha"

    class PATHS:
        program_path = f"{dirname(abspath(sys.argv[0]))}"

        assets_dir = f"{program_path}\\assets"
        cache_dir = f"{program_path}\\cache"
        plugin_dir = f"{program_path}\\plugins"

        config_file = f"{program_path}\\config.yaml"

        site_packages_folder = f"{program_path}/lib/site-packages"

    class TAGS:
        startup_window = "startup_window"
        main_window = "main_window"
        tab_bar = "tab_bar"
        menu_bar = "menu_bar"


def load(path=CONSTANTS.PATHS.config_file):
    global CONFIG
    CONFIG = Config()
    CONFIG.from_dict(yaml.safe_load(open(path)))


def save():
    yaml.safe_dump({key: getattr(CONFIG, key)
                    for key in list(CONFIG.__annotations__.keys())},
                   open(CONSTANTS.PATHS.config_file, "w"))


if exists(CONSTANTS.PATHS.config_file) and not isdir(CONSTANTS.PATHS.config_file):
    load()
else:
    CONFIG = Config()
