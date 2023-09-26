from pathlib import Path
from pyosutools.database import Osudb
from osrparse import Replay, GameMode, Mod
from datetime import datetime
from os import PathLike
from typing import List, Callable, Tuple

from lib.plugin.loader import get_plugins
from config import CONFIG
from utils import get_osu_db_cached

DEFAULT_REPLAY = Replay(GameMode(0), 0, "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, False, Mod(0), [], datetime.now(), [], 0, None)


class PluginFunctions:
    on_start: List[Tuple[Callable, int]] = []
    on_replay_preload: List[Tuple[Callable, int]] = []
    on_replay_postload: List[Tuple[Callable, int]] = []
    on_replay_presave: List[Tuple[Callable, int]] = []
    on_replay_postsave: List[Tuple[Callable, int]] = []
    on_data_update: List[Tuple[Callable, int]] = []
    on_frame_update: List[Tuple[Callable, int]] = []
    on_window_build: List[Tuple[Callable, int]] = []


class AppGlobals:
    osu_db: Osudb

    replay: Replay
    replay_path: PathLike

    plugins: List
    plugin_funcs: PluginFunctions

    data_update_func: Callable = lambda: None

    def __init__(self) -> None:
        self.plugin_funcs = PluginFunctions()


app_globals = AppGlobals()


def init_globals():
    app_globals.osu_db = get_osu_db_cached(Path(CONFIG.osu_path) / "osu!.db")
    app_globals.replay = DEFAULT_REPLAY
    app_globals.replay_path = None
    app_globals.plugins = [plugin for name, plugin in get_plugins().items() if name.split(".")[-1:][0] in CONFIG.enabled_plugins]
