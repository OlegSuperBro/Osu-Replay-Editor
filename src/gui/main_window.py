import dearpygui.dearpygui as dpg
import os
from datetime import datetime
from pyosutools.db.osu import parse_osudb
from pathlib import Path
from osrparse import Replay
from osrparse.utils import GameMode, Mod

from config import CONFIG
from gui.dpg_windows import InformationWindow, CliCommandWindow, LifeBarGraphWindow, AttributesWindow


class MainWindow():
    def __init__(self) -> None:
        self.osu_db = parse_osudb(Path(CONFIG.osu_path) / "osu!.db", sql_check_same_thread=False)
        # self.osu_db = None
        self.orig_replays = []
        self.curr_replay = Replay(GameMode(0), 0, "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, False, Mod(0), [], datetime.now(), [], 0, None)
        self.replay_path = None

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

        with dpg.file_dialog(directory_selector=False, tag="save_file_dialog", min_size=(250, 250), default_filename="replay", default_path=Path(CONFIG.osu_path) / "Replays", show=False, callback=(lambda x, y: [self.save_replay(list(y.values())[0]), dpg.configure_item("save_file_dialog", show=False)]), cancel_callback=lambda x, y: dpg.configure_item("save_file_dialog", show=False)):
            dpg.add_file_extension(".osr")
            dpg.add_file_extension("")

        with dpg.file_dialog(directory_selector=False, tag="open_file_dialog", min_size=(250, 250), default_path=Path(CONFIG.osu_path) / "Replays", show=False, callback=(lambda x, y: [self.open_replay(list(y.values())[0]), dpg.configure_item("open_file_dialog", show=False)]), cancel_callback=lambda x, y: dpg.configure_item("open_file_dialog", show=False)):
            dpg.add_file_extension(".osr")
            dpg.add_file_extension("")

        self.build_attr()
        self.build_life()
        self.build_CLI()
        self.build_info()

    def build_attr(self):
        if dpg.does_item_exist("attr_window"):
            dpg.show_item(self.attr_window._id)
            dpg.focus_item("attr_window")
            return

        self.attr_window = AttributesWindow(self.on_update)

    def build_life(self):
        if dpg.does_item_exist("life_window"):
            dpg.show_item(self.life_window._id)
            dpg.focus_item("life_window")
            return

        self.life_window = LifeBarGraphWindow()

    def build_CLI(self):
        if dpg.does_item_exist("CLI_window"):
            dpg.show_item(self.cli_window._id)
            dpg.focus_item("CLI_command")
            return

        self.cli_window = CliCommandWindow()

    def build_info(self):
        if dpg.does_item_exist("info_window"):
            dpg.show_item(self.info_window._id)
            dpg.focus_item("info_window")
            return

        self.info_window = InformationWindow()

    def on_update(self):
        self.attr_window.read_in_replay(self.curr_replay)

        self.info_window.update(self.osu_db, self.curr_replay)
        self.cli_window.update(self.curr_replay)

    def save_replay(self, path=None):
        if self.curr_replay is None:
            self.show_error("Please, open replay before saving")
            return
        if path is None:
            path = self.replay_path

        self.attr_window.read_in_replay(self.curr_replay)
        self.life_window.read_in_replay(self.curr_replay)

        self.curr_replay.write_path(path)

    def save_as_replay(self):
        if self.curr_replay is None:
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
        replay = Replay.from_path(path)
        self.orig_replays.append(replay)
        self.curr_replay = replay
        self.load_from_replay()

        self.info_window.update_on_load(self.osu_db, self.curr_replay)
        self.cli_window.update_on_load(self.curr_replay)

    def load_from_replay(self):
        self.attr_window.load_from_replay(self.curr_replay)
        self.life_window.load_from_replay(self.curr_replay)
