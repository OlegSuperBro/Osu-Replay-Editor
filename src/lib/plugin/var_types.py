from typing import TypeVar as _TypeVar, Callable as _Callable
from osrparse import Replay as _Replay
from pyosutools.database import Osudb as _Osudb

MainWindow = _TypeVar("MainWindow", str, None)
TabBar = _TypeVar("TabBar", str, None)
Replay = _TypeVar("Replay", _Replay, None)
ReplayPath = _TypeVar("ReplayPath", str, None)
Osudb = _TypeVar("Osudb", _Osudb, None)
UpdateFunc = _TypeVar("UpdateFunc", _Callable, None)


def _get_all():
    # https://stackoverflow.com/a/28150307
    return [value for key, value in globals().items() if not (key.startswith('__') or key.startswith('_'))]
