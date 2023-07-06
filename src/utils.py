import datetime
import numpy as np
from aenum import IntFlag, Enum
from pathlib import Path
from osrparse.utils import LifeBarState
from typing import List

import osrparse


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


CLI_START_COMMAND = f"py \"{Path(__file__).parent}\\CLI.py\""


def mods_list() -> list[str]:
    mod_list = list(map(lambda c: c.name, Mod))
    mod_list.remove("Target")  # it will break replay
    return mod_list


def code2gamemode(code: int) -> str:
    return GameMode(code).name


def gamemode2code(mode: str) -> int:
    return GameMode[mode].value


def mods2code(mods: list[str]) -> int:
    if len(mods) == 0:
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
        assert int(value) == float(value)
    except (AssertionError, ValueError, TypeError):
        return False
    else:
        return True


def lifebar2str(lifebar: List[LifeBarState]):
    return ",".join([f"{state.time}|{state.life}" for state in lifebar])[:-1]


def generate_command(input_path: str = None, nickname: str = None, n300: int = None, n100: int = None, n50: int = None, ngekis: int = None, nkatus: int = None, nmisses: int = None,
                     score: int = None, maxcombo: int = None, pfc: bool = None, mods: str = None, rawmods: int = None, time: int = None, lifebar: str = None, output: str = None) -> str:
    command = CLI_START_COMMAND

    if input_path is not None:
        command += f" \"{input_path}\""

    else:
        command += " \"[path]\""

    if nickname is not None:
        command += f" --nickname {nickname}"

    if n300 is not None:
        command += f" --n300 {n300}"

    if n100 is not None:
        command += f" --n100 {n100}"

    if n50 is not None:
        command += f" --n50 {n50}"

    if ngekis is not None:
        command += f" --ngekis {ngekis}"

    if nkatus is not None:
        command += f" --nkatus {nkatus}"

    if nmisses is not None:
        command += f" --nmisses {nmisses}"

    if score is not None:
        command += f" --score {score}"

    if maxcombo is not None:
        command += f" --maxcombo {maxcombo}"

    if pfc is not None:
        command += f" --pfc {pfc}"

    if mods is not None:
        command += f" --mods {mods}"

    if rawmods is not None:
        command += f" --rawmods {rawmods}"

    if time is not None:
        command += f" --time {time}"

    if lifebar is not None:
        command += f" --lifebar \"{lifebar}\""

    if output is not None:
        command += f" -o \"{output}\""

    return command


def dist_point_to_segment(p, s0, s1):
    """
    Get the distance from the point *p* to the segment (*s0*, *s1*), where
    *p*, *s0*, *s1* are ``[x, y]`` arrays.
    """
    s01 = s1 - s0
    s0p = p - s0
    if (s01 == 0).all():
        return np.hypot(*s0p)
    # Project onto segment, without going past segment ends.
    p1 = s0 + np.clip((s0p @ s01) / (s01 @ s01), 0, 1) * s01
    return np.hypot(*(p - p1))


def decrease_lifebar_length(lifebar: List[LifeBarState]):
    new_lifebar = []
    for index in range(len(lifebar)):
        if index == 0 or index >= len(lifebar) - 1:
            print(True)
            new_lifebar.append(lifebar[index])
            continue

        if lifebar[index].life != lifebar[index + 1].life or lifebar[index].life != lifebar[index - 1].life:
            new_lifebar.append(lifebar[index])

    return new_lifebar
