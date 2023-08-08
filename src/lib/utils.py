import datetime
from aenum import IntFlag, Enum
from os import mkdir, PathLike
from os.path import dirname, exists, isdir
from osrparse.utils import LifeBarState
from typing import List, Any
from pyosutools.database import Osudb

from config import CONSTANTS


class GameMode(Enum):
    """
    Literaly same as Gamemode from osrparse, except this one uses aenum.Enum, except enum.Enum
    """
    STD = 0
    TAIKO = 1
    CTB = 2
    MANIA = 3


class Mod(IntFlag):
    """
    Literaly same as Mod from osrparse, except this one uses aenum.IntFlag, except enum.IntFlag
    """
    NoMod = 0
    NoFail = 1 << 0
    Easy = 1 << 1
    TouchDevice = 1 << 2
    Hidden = 1 << 3
    HardRock = 1 << 4
    SuddenDeath = 1 << 5
    DoubleTime = 1 << 6
    Relax = 1 << 7
    HalfTime = 1 << 8
    Nightcore = 1 << 9
    Flashlight = 1 << 10
    Autoplay = 1 << 11
    SpunOut = 1 << 12
    Autopilot = 1 << 13
    Perfect = 1 << 14
    Key4 = 1 << 15
    Key5 = 1 << 16
    Key6 = 1 << 17
    Key7 = 1 << 18
    Key8 = 1 << 19
    FadeIn = 1 << 20
    Random = 1 << 21
    Cinema = 1 << 22
    Target = 1 << 23
    Key9 = 1 << 24
    KeyCoop = 1 << 25
    Key1 = 1 << 26
    Key3 = 1 << 27
    Key2 = 1 << 28
    ScoreV2 = 1 << 29
    Mirror = 1 << 30


def mods_list() -> list[str]:
    mod_list = list(map(lambda c: c.name, Mod))
    mod_list.remove("Target")  # it will break replay
    return mod_list


def code2gamemode(code: int) -> str:
    return GameMode(code).name


def gamemode2code(mode: str) -> int:
    return GameMode[mode].value


def mods2code(mods: list[str]) -> int:
    if not mods:
        return 0
    return Mod["|".join(mods)].value


def code2mods(code: int) -> str:
    return Mod(code).name.split("|")


def windows_ticks2date(ticks: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp((ticks-621355968000000000)/10_000_000, tz=datetime.timezone.utc)


def date2windows_ticks(date: datetime.datetime):
    return int(date.timestamp() * 10_000_000 + 621355968000000000)


def get_from_tree(dictionary: dict, *path: any) -> any:
    value = dictionary
    for key in path:
        try:
            value = value.get(key)
        except KeyError:
            return None
    return value


def is_int(value: Any):
    try:
        assert float(value).is_integer() and value.find("e") == -1
    except (AssertionError, ValueError, TypeError):
        return False
    else:
        return True


def lifebar2str(lifebar: List[LifeBarState]):
    return ",".join([f"{state.time}|{state.life}" for state in lifebar])[:-1]


def get_osu_db_cached(db_path: PathLike) -> Osudb:
    cache_path = f"{CONSTANTS.PATHS.cache_dir}/beatmaps_cache.pickle"
    if not isdir(dirname(cache_path)):
        mkdir(dirname(cache_path))

    if exists(cache_path):
        tmp = Osudb.from_path(db_path, skip_beatmaps=True)
        tmp.load_cache_beatmaps(cache_path)
        return tmp

    return Osudb.from_path(db_path)


def save_osu_db_cache(osudb: Osudb) -> None:
    cache_path = f"{CONSTANTS.PATHS.cache_dir}/beatmaps_cache.pickle"
    if not isdir(dirname(cache_path)):
        mkdir(dirname(cache_path))
    osudb.save_cache_beatmaps(cache_path)
