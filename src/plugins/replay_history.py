from lib.plugin.utils import on_window_build, on_replay_postload
from lib.plugin import var_types
from lib.utils import set_current_replay

from dearpygui import dearpygui as dpg
from pyosutools.datatypes import BeatmapDB
from pyosutools.database import Osudb

from osrparse import Replay
from typing import List

replays: List[Replay] = []
ignore_load: bool = False


def get_beatmap_by_hash(beatmaps: List[BeatmapDB], beatmap_hash: str) -> BeatmapDB:
    return next(
        (beatmap for beatmap in beatmaps if beatmap_hash == beatmap.md5_hash),
        None,
    )


@on_window_build()
def on_window_load():
    with dpg.window(tag="replays_history_win", width=200, no_resize=True):
        dpg.add_listbox([], tag="replays_history_list", callback=list_callback, width=-1, num_items=10)


@on_replay_postload()
def on_new_replay(replay: var_types.Replay, osudb: var_types.Osudb):
    if ignore_load:
        return

    if replay in replays:
        replays.remove(replay)

    replays.insert(0, replay)
    update_window(osudb)


def update_window(osudb: Osudb):
    tmp_list = []
    for index, replay in enumerate(replays):
        tmp_beatmap = get_beatmap_by_hash(osudb.beatmaps, replay.beatmap_hash)
        tmp_list.append(f"{index} > {replay.username} - {tmp_beatmap.artist} - {tmp_beatmap.title}")
    dpg.configure_item("replays_history_list", items=tmp_list)

    dpg.set_value("replays_history_list", 0)


def list_callback():
    global ignore_load
    ignore_load = True
    set_current_replay(replays[int(dpg.get_value("replays_history_list").split(">")[0])])
    ignore_load = False
