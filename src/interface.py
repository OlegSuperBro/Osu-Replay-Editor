import dearpygui.dearpygui as dpg
import os
import datetime
import pyperclip
from math import ceil
from pyosutools.db.osu import parse_osudb
from pathlib import Path
from osrparse import Replay
from osrparse.utils import LifeBarState

import utils
from utils import Mod
import calculation
from config import CONFIG


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


class MainWindow():
    def __init__(self) -> None:
        self.osu_db = parse_osudb(Path(CONFIG.get("osu_path")) / "osu!.db", sql_check_same_thread=False)
        # self.osu_db = None
        self.replay = None
        self.replay_path = None

        self.lifebar_graph_dict = {}

        dpg.create_context()
        if os.path.exists("dpg.ini"):
            dpg.configure_app(init_file="dpg.ini")
        dpg.create_viewport(title='Replay Editor', width=1500, height=900)

        self.build_window()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def build_window(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open", callback=lambda: dpg.configure_item("open_file_dialog", show=True))
                dpg.add_menu_item(label="Save", callback=lambda: self.save_replay(self.replay_path))
                dpg.add_menu_item(label="Save as...", callback=lambda: self.save_as_replay())
            with dpg.menu(label="View"):
                with dpg.menu(label="Show"):
                    dpg.add_menu_item(label="Attributes editor", callback=self.build_attr)
                    dpg.add_menu_item(label="Life graph editor", callback=self.build_life)
                    # dpg.add_menu_item(label="Data editor")
                    dpg.add_menu_item(label="Replay information", callback=self.build_info)
                    dpg.add_menu_item(label="CLI command", callback=self.build_CLI)

        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=250, height=100):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        with dpg.file_dialog(directory_selector=False, tag="save_file_dialog", min_size=(250, 250), default_filename="replay", default_path=Path(CONFIG.get("osu_path")) / "Replays", show=False, callback=(lambda x, y: [self.save_replay(list(y.values())[0]), dpg.configure_item("save_file_dialog", show=False)]), cancel_callback=lambda x, y: dpg.configure_item("save_file_dialog", show=False)):
            dpg.add_file_extension(".osr")
            dpg.add_file_extension("")

        with dpg.file_dialog(directory_selector=False, tag="open_file_dialog", min_size=(250, 250), default_path=Path(CONFIG.get("osu_path")) / "Replays", show=False, callback=(lambda x, y: [self.open_replay(list(y.values())[0]), dpg.configure_item("open_file_dialog", show=False)]), cancel_callback=lambda x, y: dpg.configure_item("open_file_dialog", show=False)):
            dpg.add_file_extension(".osr")
            dpg.add_file_extension("")

        self.build_attr()
        self.build_life()
        self.build_CLI()
        self.build_info()

    def build_attr(self, sender=None, user_data=None):
        if dpg.does_item_exist("attr_window") is True:
            dpg.focus_item("attr_window")
            return
        with dpg.window(label="Attributes", pos=(0, 20), min_size=(650, 100), tag="attr_window", on_close=lambda sender: None if sender != "attr_window" else dpg.delete_item("attr_window")):
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
                    dpg.add_input_text(multiline=True, height=90, tab_input=True, tag="username", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="300s", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="100s", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="50s", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="gekis", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="katus", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="misses", callback=self.update_info_window)
                    dpg.add_input_int(max_value=2147483647, max_clamped=True, tag="total_score", callback=self.update_info_window)
                    dpg.add_input_int(max_value=65535, max_clamped=True, tag="max_combo", callback=self.update_info_window)
                    dpg.add_checkbox(tag="perfect_combo", callback=self.update_info_window)
                    with dpg.tree_node(label="Date picker"):
                        dpg.add_time_picker(tag="time", callback=self.update_info_window)
                        dpg.add_date_picker(default_value={"month_day": datetime.date.today().day, "year": datetime.date.today().year-2000 + 100, "month": datetime.date.today().month}, tag="date", callback=self.update_info_window)  # Date
                    dpg.add_spacer(height=5)
                    with dpg.tree_node(label="Mods"):
                        generate_mods_checkboxes(5, self.update_info_window)

    def build_life(self, sender=None, user_data=None):
        if dpg.does_item_exist("life_window") is True:
            dpg.focus_item("life_window")
            return
        with dpg.window(label="Life Graph", pos=(0, 400), width=650, height=405, min_size=(500, 250), tag="life_window", on_close=lambda: dpg.delete_item("life_window")):
            with dpg.plot(height=-1, width=-1, tag="life_graph"):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.set_axis_limits("y_axis", 0, 1)

    def build_CLI(self, sender=None, user_data=None):
        if dpg.does_item_exist("CLI_window") is True:
            dpg.focus_item("CLI_command")
            return
        with dpg.window(label="CLI command", pos=(0, 807), width=650, min_size=(400, 50), no_scrollbar=True, max_size=(30000, 50), tag="CLI_window", on_close=lambda: dpg.delete_item("CLI_window")):
            with dpg.group(horizontal=True):
                dpg.add_input_text(width=-135, readonly=True, tag="cli_command")
                dpg.add_button(label="Copy to clipboard", callback=self.clipboard_copy_CLI_command)

    def build_info(self, sender=None, user_data=None):
        if dpg.does_item_exist("info_window") is True:
            dpg.focus_item("info_window")
            return

        with dpg.window(label="Replay Information", pos=(650, 20), width=835, min_size=(250, 250), tag="info_window", on_close=lambda: dpg.delete_item("info_window")):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Beatmap name")
                    dpg.add_spacer()
                    dpg.add_text("Total accuracy")
                    dpg.add_text("Total pp")
                with dpg.group():
                    dpg.add_text(tag="beatmap_name")
                    dpg.add_text(tag="total_accuracy")
                    dpg.add_text(tag="total_pp")

    def update_info_window(self, sender=None, user_data=None):
        n300 = dpg.get_value("300s")
        n100 = dpg.get_value("100s")
        n50 = dpg.get_value("50s")
        n_geki = dpg.get_value("gekis")
        n_katu = dpg.get_value("katus")
        n_miss = dpg.get_value("misses")
        max_combo = dpg.get_value("max_combo")

        beatmap_name = "None"
        acc = calculation.calculate_acc(n300, n100, n50, n_miss)
        pp = 0

        if self.replay is not None:
            beatmap = self.osu_db.get_beatmap_from_hash(self.replay.beatmap_hash)
            beatmap_name = f"{beatmap.artist} / {beatmap.title}"
            beatmap_path = str(Path(CONFIG.get("osu_path")) / "songs" / beatmap.folder_name / beatmap.osu_file)
            pp = calculation.calculate_pp(beatmap_path, mode=self.replay.mode, mods=Mod(self.get_mods()), n_geki=n_geki, n_katu=n_katu, n300=n300, n100=n100, n50=n50, n_misses=n_miss, combo=max_combo)

        dpg.set_value("beatmap_name", beatmap_name)
        dpg.set_value("total_accuracy", acc)
        dpg.set_value("total_pp", f"{str(pp)}pp")
        dpg.set_value("cli_command", self.generate_CLI_command())

    def generate_CLI_command(self, output_path: str = "[output]"):
        date = dpg.get_value("date")
        time = dpg.get_value("time")
        date_time = datetime.datetime.strptime(f'{date.get("year") - 100 + 2000}/{date.get("month")}/{date.get("month_day")} {time.get("hour")}:{time.get("min")}:{time.get("sec")}', "%Y/%m/%d %H:%M:%S")
        lifebar = utils.lifebar2str([LifeBarState(int(state.get("x")), round(state.get("y"), 2)) for state in self.lifebar_graph_dict.values()]) if self.replay is not None else None
        return utils.generate_command(self.replay_path,
                                      dpg.get_value("username"), dpg.get_value("300s"), dpg.get_value("100s"), dpg.get_value("50s"), dpg.get_value("gekis"), dpg.get_value("katus"), dpg.get_value("misses"),
                                      dpg.get_value("total_score"),  dpg.get_value("max_combo"),  dpg.get_value("perfect_combo"), None, self.get_mods(), utils.date2windows_ticks(date_time), lifebar, output=output_path)

    def clipboard_copy_CLI_command(self):
        pyperclip.copy(self.generate_CLI_command())

    def get_mods(self):
        mods = 0
        for mod in utils.mods_list():
            if dpg.get_value(f"mod_{mod}") is True:
                mods += Mod[mod].value
        return mods

    def save_replay(self, path=None):
        if self.replay is None:
            self.show_error("Please, open replay before saving")
            return
        if path is None:
            path = self.replay_path
        os.system(self.generate_CLI_command(path))

    def save_as_replay(self):
        if self.replay is None:
            self.show_error("Please, open replay before saving")
            return

        dpg.show_item("save_file_dialog")

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)

    def open_replay(self, path):
        if path is None:
            return
        self.replay_path = path
        self.replay = Replay.from_path(path)
        self.load_from_replay()
        self.update_info_window()

    def load_from_replay(self):
        dpg.set_value("username", self.replay.username)
        dpg.set_value("300s", self.replay.count_300)
        dpg.set_value("100s", self.replay.count_100)
        dpg.set_value("50s", self.replay.count_50)
        dpg.set_value("gekis", self.replay.count_geki)
        dpg.set_value("katus", self.replay.count_katu)
        dpg.set_value("misses", self.replay.count_miss)
        dpg.set_value("total_score", self.replay.score)
        dpg.set_value("max_combo", self.replay.max_combo)
        dpg.set_value("perfect_combo", self.replay.perfect)
        dpg.set_value("date", {"month_day": self.replay.timestamp.day, "year": self.replay.timestamp.year-2000 + 100, "month": self.replay.timestamp.month})
        dpg.set_value("time", {"hour": self.replay.timestamp.hour, "min": self.replay.timestamp.minute, "sec": self.replay.timestamp.second})

        for mod in utils.mods_list():
            dpg.set_value(f"mod_{mod}", Mod[mod] in Mod(self.replay.mods))

        lifebar = utils.decrease_lifebar_length(self.replay.life_bar_graph)
        self.lifebar_graph_dict.clear()
        for index, x, y in zip(range(len(lifebar)), [life_state.time for life_state in lifebar], [life_state.life for life_state in lifebar]):
            dpg.delete_item(f"point_{index}")
            self.change_lifebar_dict(f"point_{index}", x, y)
            dpg.add_drag_point(parent="life_graph", default_value=(x, y), label=index, tag=f"point_{index}", callback=lambda x, y: self.change_lifebar_dict(dpg.get_item_alias(x), dpg.get_value(x)[0], dpg.get_value(x)[1]))
        dpg.set_axis_limits("x_axis", 0, x)

    def change_lifebar_dict(self, label, x, y):
        self.lifebar_graph_dict[label] = {"x": x, "y": y}

        dpg.delete_item("life_graph_line")
        dpg.draw_polyline([[value.get("x"), value.get("y")] for value in self.lifebar_graph_dict.values()], thickness=2, tag="life_graph_line", parent="life_graph")


if __name__ == "__main__":
    try:
        app = MainWindow()
    except Exception as e:
        print(e)
    finally:
        # dpg.save_init_file("dpg.ini")
        pass
