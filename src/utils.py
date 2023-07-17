import datetime
from aenum import IntFlag, Enum
from pathlib import Path
from os import mkdir
from os.path import dirname, exists, isdir
from osrparse.utils import LifeBarState
from typing import List
from pyosutools.db.osu import Osudb, parse_osudb


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


def is_int(value: any):
    try:
        assert float(value).is_integer()
    except (AssertionError, ValueError, TypeError):
        return False
    else:
        return True


def lifebar2str(lifebar: List[LifeBarState]):
    return ",".join([f"{state.time}|{state.life}" for state in lifebar])[:-1]


def decrease_lifebar_length(lifebar: List[LifeBarState]) -> List[LifeBarState]:
    new_lifebar = []
    for index in range(len(lifebar)):
        if index == 0 or index >= len(lifebar) - 1:
            new_lifebar.append(lifebar[index])
            continue

        if lifebar[index].life != lifebar[index + 1].life or lifebar[index].life != lifebar[index - 1].life:
            new_lifebar.append(lifebar[index])

    return new_lifebar


def get_osu_db_cached(db_path) -> Osudb:
    cache_path = Path(dirname(__file__)) / "cache" / "beatmaps_cache.db"
    if not isdir(dirname(cache_path)):
        mkdir(dirname(cache_path))
    return parse_osudb(db_path, cache_path, exists(cache_path), sql_check_same_thread=False)
