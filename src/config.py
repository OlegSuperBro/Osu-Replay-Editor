import yaml
import inspect
import contextlib
import sys
from dataclasses import dataclass
from os.path import abspath, dirname


@dataclass
class CONFIG:
    osu_path: str = "C:\\Games\\osu!"
    skin: str = "Default"

    @classmethod
    def from_dict(cls, env: dict):
        for key, value in {k: v for k, v in env.items() if k in inspect.signature(cls).parameters}.items():
            setattr(cls, key, value)


class CONSTANTS:
    program_path = f"{dirname(abspath(sys.argv[0]))}"

    assets_dir = f"{program_path}\\assets"
    cache_dir = f"{program_path}\\cache"

    skins_dir = f"{assets_dir}\\Skins"
    default_skin_path = f"{assets_dir}\\Skins\\Default"

    config_file = f"{program_path}\\config.yaml"
    dpg_config_file = f"{program_path}\\dearpygui.ini"


with contextlib.suppress(FileNotFoundError):
    CONFIG.from_dict(yaml.safe_load(open(CONSTANTS.config_file, "r")))


def save():
    yaml.safe_dump({key: CONFIG.__dict__.get(key)
                    for key in list(CONFIG.__annotations__.keys())},
                   open(CONSTANTS.config_file, "w"))
