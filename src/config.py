import yaml
import inspect
from dataclasses import dataclass

CONFIG_PATH = "config.yaml"


@dataclass
class Config:
    osu_path: str = "C:/Games/osu!/"

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })


try:
    CONFIG = Config.from_dict(yaml.safe_load(open(CONFIG_PATH, "r")))
except FileNotFoundError:
    CONFIG = Config()


def save():
    yaml.safe_dump(dict(CONFIG), open(CONFIG_PATH, "w"))
