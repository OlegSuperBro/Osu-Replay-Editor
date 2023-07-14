import dearpygui.dearpygui as dpg
import datetime
from math import ceil
from osrparse import Replay

import utils
from utils import Mod


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


class AttributesWindow:
    def __init__(self, callback) -> None:
        self._id = self._build(callback)

    def _build(self, callback) -> None:
        with dpg.window(label="Attributes", pos=(0, 20), min_size=(650, 100), tag="attr_window", on_close=lambda sender: None if sender != "attr_window" else dpg.hide_item("attr_window")) as _id:
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
                    dpg.add_text("Date and time")
                    dpg.add_text("Mods")
                with dpg.group():
                    dpg.add_input_text(multiline=True, height=90, tab_input=True, tag="username", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="300s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="100s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="50s", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="gekis", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="katus", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="misses", callback=callback)
                    dpg.add_input_int(max_value=2147483647, max_clamped=True, tag="total_score", callback=callback)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="max_combo", callback=callback)
                    dpg.add_checkbox(tag="perfect_combo", callback=callback)
                    with dpg.tree_node(label="Date picker"):
                        dpg.add_time_picker(tag="time", callback=callback)
                        dpg.add_date_picker(default_value={"month_day": datetime.date.today().day, "year": datetime.date.today().year-2000 + 100, "month": datetime.date.today().month}, tag="date", callback=callback)  # Date
                    dpg.add_spacer(height=5)
                    with dpg.tree_node(label="Mods"):
                        generate_mods_checkboxes(5, callback)
            return _id

    def load_from_replay(self, replay: Replay):
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
            dpg.set_value(f"mod_{mod}", Mod[mod] in Mod(replay.mods))

    def read_in_replay(self, replay: Replay) -> None:
        replay.username = dpg.get_value("username")
        replay.count_300 = dpg.get_value("300s")
        replay.count_100 = dpg.get_value("100s")
        replay.count_50 = dpg.get_value("50s")
        replay.count_geki = dpg.get_value("gekis")
        replay.count_katu = dpg.get_value("katus")
        replay.count_miss = dpg.get_value("misses")
        replay.score = dpg.get_value("total_score")
        replay.max_combo = dpg.get_value("max_combo")
        replay.perfect = dpg.get_value("perfect_combo")

        date = dpg.get_value("date")
        time = dpg.get_value("time")

        replay.timestamp = datetime.datetime.strptime(f'{date.get("year") - 100 + 2000}/{date.get("month")}/{date.get("month_day")} {time.get("hour")}:{time.get("min")}:{time.get("sec")}', "%Y/%m/%d %H:%M:%S")
        replay.mods = self.get_mods()

    def get_mods(self) -> Mod:
        mods = 0
        for mod in utils.mods_list():
            if dpg.get_value(f"mod_{mod}"):
                mods += Mod[mod].value
        return Mod(mods)
