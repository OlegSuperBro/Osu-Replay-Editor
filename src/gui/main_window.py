import dearpygui.dearpygui as dpg
import os
from datetime import datetime
from pathlib import Path
from osrparse import Replay
from osrparse.utils import GameMode, Mod
from tkinter.filedialog import askopenfilename, asksaveasfilename

from config import CONFIG
from utils import get_osu_db_cached
from gui.dpg_windows import InformationWindow, LifeBarGraphWindow, AttributesWindow


class MainWindow():
    default_title = "Replay Editor"

    def __init__(self, replay: str = None) -> None:
        self.osu_db = get_osu_db_cached(Path(CONFIG.osu_path) / "osu!.db")
        self.curr_replay = Replay(GameMode(0), 0, "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, False, Mod(0), [], datetime.now(), [], 0, None)
        self.replay_path = None

        if replay is not None:
            try:
                self.curr_replay = Replay.from_path(replay)
                self.replay_path = replay
            except Exception as e:
                print(e)

        dpg.create_context()
        if os.path.exists("dpg.ini"):
            dpg.configure_app(init_file="dpg.ini")
        dpg.create_viewport(title=self.default_title, width=1500, height=900)

        self.build_window()

        if self.replay_path is not None:
            self.open_replay(self.replay_path)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def build_window(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open", callback=lambda: self.open_replay(askopenfilename(defaultextension=".osr", filetypes=[("Osu! Replay", ".osr"), ("All files", "")], initialdir=CONFIG.osu_path + "\\Replays")))
                dpg.add_menu_item(label="Save", callback=lambda: self.save_replay(self.replay_path))
                dpg.add_menu_item(label="Save as...", callback=lambda: self.save_replay(asksaveasfilename(defaultextension=".osr", filetypes=[("Osu! Replay", ".osr"), ("All files", "")], initialdir=CONFIG.osu_path, initialfile="replay")))
            with dpg.menu(label="View"):
                with dpg.menu(label="Show"):
                    dpg.add_menu_item(label="Attributes editor", callback=self.build_attr)
                    dpg.add_menu_item(label="Life graph editor", callback=self.build_life)
                    # dpg.add_menu_item(label="Data editor")
                    dpg.add_menu_item(label="Replay information", callback=self.build_info)

        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=400, height=150):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        self.build_attr()
        self.build_life()
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

    def build_info(self):
        if dpg.does_item_exist("info_window"):
            dpg.show_item(self.info_window._id)
            dpg.focus_item("info_window")
            return

        self.info_window = InformationWindow()

    def on_update(self):
        self.attr_window.read_in_replay(self.curr_replay)

        self.info_window.update(self.osu_db, self.curr_replay)

    def save_replay(self, path=None):
        if self.curr_replay.game_version == 0:
            self.show_error("Please, open replay before saving")
            return
        if path is None:
            path = self.replay_path
        elif path == "":
            self.show_error("Please, select a file")
            return

        self.attr_window.read_in_replay(self.curr_replay)
        self.life_window.read_in_replay(self.curr_replay)

        self.curr_replay.write_path(path)

        self.replay_path = path
        dpg.set_viewport_title(f"{self.default_title} {self.replay_path}")

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)

    def open_replay(self, path):
        if path == "":
            return
        try:
            replay = Replay.from_path(path)
        except Exception as e:
            self.show_error(f"Error occured: \n\n{e} \n\nPossibly, replay is corrupted")
            return
        self.replay_path = path
        self.curr_replay = replay
        self.load_from_replay()

        self.info_window.update_on_load(self.osu_db, self.curr_replay)

        dpg.set_viewport_title(f"{self.default_title} {self.replay_path}")

    def load_from_replay(self):
        self.attr_window.load_from_replay(self.curr_replay)
        self.life_window.load_from_replay(self.curr_replay)
