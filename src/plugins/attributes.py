import dearpygui.dearpygui as dpg
import datetime
from math import ceil
from osrparse import Replay
from pathlib import Path
from pyosutools.datatypes import BeatmapDB
from pyosutools.database import Osudb
from typing import List

import lib.utils as utils
import lib.calculation as calculation
from lib.plugin import utils as plugin_utils, var_types
from config import CONFIG


def get_beatmap_by_hash(beatmaps: List[BeatmapDB], beatmap_hash: str) -> BeatmapDB:
    return next(
        (beatmap for beatmap in beatmaps if beatmap_hash == beatmap.md5_hash),
        None,
    )


def generate_mods_checkboxes(width, callback):
    mod_list = utils.mods_list()

    height = ceil(len(mod_list) / width)

    mod_index = 0

    with dpg.table(header_row=False):
        for _ in range(width):
            dpg.add_table_column()

        for _ in range(height):
            with dpg.table_row():
                for _ in range(width):
                    try:
                        mod = mod_list[mod_index]
                        mod_index += 1
                    except IndexError:
                        mod_index += 1
                        continue
                    dpg.add_checkbox(label=mod, tag=f"mod_{mod}", callback=callback)


class Tab:
    def __init__(self) -> None:
        self._id = None

    def build(self, callback) -> None:
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Player")
                    dpg.add_spacer(height=67)
                    dpg.add_text("300s")
                    dpg.add_text("100s")
                    dpg.add_text("50s")
                    dpg.add_text("Gekis")
                    dpg.add_text("Katus")
                    dpg.add_text("Misses")
                    dpg.add_text("Total score")
                    dpg.add_text("Max combo")
                    dpg.add_text("Perfect combo")
                    dpg.add_spacer(height=5)
                    dpg.add_text("Date and time")
                    dpg.add_spacer(height=160)
                    dpg.add_text("Mods")
                with dpg.group(width=600):
                    dpg.add_input_text(multiline=True, height=90, tab_input=True, tag="username", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="300s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="100s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="50s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="gekis", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="katus", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="misses", callback=callback)
                    dpg.add_input_text(tag="total_score", callback=lambda: [self.verify_score(), callback()])  # stupid int overflow :(
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="max_combo", callback=callback)
                    dpg.add_checkbox(tag="perfect_combo", callback=callback)

                    dpg.add_spacer(height=5)
                    dpg.add_date_picker(default_value={"month_day": datetime.date.today().day, "year": datetime.date.today().year-2000 + 100, "month": datetime.date.today().month}, tag="date", callback=callback)  # Date

                    dpg.add_time_picker(tag="time", callback=callback)

                    dpg.add_spacer(height=5)
                    with dpg.child_window(label="Mods", width=550, height=175, no_scrollbar=True, menubar=True):
                        with dpg.menu_bar():
                            dpg.add_text("Mods")
                        generate_mods_checkboxes(5, callback)

            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Beatmap name")
                    dpg.add_text("Total accuracy")
                    dpg.add_text("Total pp")
                with dpg.group():
                    dpg.add_text(tag="beatmap_name")
                    dpg.add_text(tag="total_accuracy")
                    dpg.add_text(tag="total_pp")

    def verify_score(self):
        value = dpg.get_value("total_score")
        if not utils.is_int(value):
            value = 0

        if int(value) >= 2147483647:
            value = 2147483647

        elif int(value) <= -2147483647:
            value = -2147483647

        dpg.set_value("total_score", value)

    def get_mods(self) -> utils.Mod:
        return utils.Mod(sum(
            utils.Mod[mod].value
            for mod in utils.mods_list()
            if dpg.get_value(f"mod_{mod}")
        ))

    def on_replay_load(self, replay: Replay):
        dpg.set_value("username", replay.username)
        dpg.set_value("300s", replay.count_300)
        dpg.set_value("100s", replay.count_100)
        dpg.set_value("50s", replay.count_50)
        dpg.set_value("gekis", replay.count_geki)
        dpg.set_value("katus", replay.count_katu)
        dpg.set_value("misses", replay.count_miss)
        dpg.set_value("total_score", replay.score)
        dpg.set_value("max_combo", replay.max_combo)
        dpg.set_value("perfect_combo", replay.perfect)
        dpg.set_value("date", {"month_day": replay.timestamp.day, "year": replay.timestamp.year-2000 + 100, "month": replay.timestamp.month})
        dpg.set_value("time", {"hour": replay.timestamp.hour, "min": replay.timestamp.minute, "sec": replay.timestamp.second})

        for mod in utils.mods_list():
            dpg.set_value(f"mod_{mod}", utils.Mod[mod] in utils.Mod(replay.mods))

    def load_in_replay(self, replay: Replay) -> None:
        replay.username = dpg.get_value("username")
        replay.count_300 = dpg.get_value("300s")
        replay.count_100 = dpg.get_value("100s")
        replay.count_50 = dpg.get_value("50s")
        replay.count_geki = dpg.get_value("gekis")
        replay.count_katu = dpg.get_value("katus")
        replay.count_miss = dpg.get_value("misses")
        replay.score = int(dpg.get_value("total_score"))
        replay.max_combo = dpg.get_value("max_combo")
        replay.perfect = dpg.get_value("perfect_combo")

        date = dpg.get_value("date")
        time = dpg.get_value("time")

        replay.timestamp = datetime.datetime.strptime(f'{date.get("year") - 100 + 2000}/{date.get("month")}/{date.get("month_day")} {time.get("hour")}:{time.get("min")}:{time.get("sec")}', "%Y/%m/%d %H:%M:%S")
        replay.mods = self.get_mods()

    def update_data(self, osu_db: Osudb, replay: Replay = None):
        acc = calculation.calculate_acc(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)
        pp = 0
        if replay.game_version != 0:
            beatmap = get_beatmap_by_hash(osu_db.beatmaps, replay.beatmap_hash)
            beatmap_path = str(Path(CONFIG.osu_path) / "songs" / beatmap.folder_name / beatmap.osu_file)
            pp = calculation.calculate_pp(beatmap_path, mode=replay.mode, mods=replay.mods,
                                          n_geki=replay.count_geki, n_katu=replay.count_katu, n300=replay.count_300,
                                          n100=replay.count_100, n50=replay.count_50, n_misses=replay.count_miss, combo=replay.max_combo)
        dpg.set_value("total_accuracy", acc)
        dpg.set_value("total_pp", f"{str(pp)}pp")

    def on_replay_post_load(self, osu_db: Osudb, replay: Replay = None):
        beatmap_name = "None"
        if replay.game_version != 0:
            beatmap = get_beatmap_by_hash(osu_db.beatmaps, replay.beatmap_hash)
            beatmap_name = f"{beatmap.artist} / {beatmap.title}"
            self.update_data(osu_db, replay)

        dpg.set_value("beatmap_name", beatmap_name)


@plugin_utils.on_start()
def on_start():
    global tab
    tab = Tab()


@plugin_utils.on_window_build()
def on_build(parent: var_types.TabBar, update_func: var_types.UpdateFunc):
    with dpg.tab(label="Attributes", tag="attr_window", parent=parent) as _id:
        tab._id = _id
        tab.build(update_func)


@plugin_utils.on_replay_postload()
def on_load(db: var_types.Osudb, replay: var_types.Replay):
    tab.on_replay_load(replay)


@plugin_utils.on_replay_postload(plugin_utils.Priority.DEFAULT + 1)
def on_post_load(db: var_types.Osudb, replay: var_types.Replay):
    tab.on_replay_post_load(db, replay)
    tab.update_data(db, replay)


@plugin_utils.on_replay_presave()
def on_save(replay: var_types.Replay):
    tab.load_in_replay(replay)


@plugin_utils.on_data_update()
def on_update(db: var_types.Osudb, replay: var_types.Replay):
    tab.load_in_replay(replay)
    tab.update_data(db, replay)


REQUIREMENTS = ["rosu-pp-py == 0.9.4"]
