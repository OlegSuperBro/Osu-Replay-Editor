import yaml

CONFIG_PATH = "config.yaml"

DEFAULT_CONFIG = \
"""
osu_path: "C:/Games/osu!/"
"""

try:
    CONFIG = yaml.safe_load(open(CONFIG_PATH, "r"))
except FileNotFoundError:
    CONFIG = yaml.safe_load(DEFAULT_CONFIG)


def save():
    yaml.safe_dump(CONFIG, open(CONFIG_PATH, "w"))
