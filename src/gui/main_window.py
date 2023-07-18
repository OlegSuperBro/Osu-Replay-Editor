import dearpygui.dearpygui as dpg
from pathlib import Path
from osrparse import Replay
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import List

from config import CONFIG
from utils import get_osu_db_cached
from gui.tools import tabs
from .template import Template


class MainWindow():
    default_title = "Replay Editor"

    def __init__(self, replay: Replay, replay_path: str) -> None:
        self.osu_db = get_osu_db_cached(Path(CONFIG.osu_path) / "osu!.db")

        self.replay = replay
        self.replay_path = replay_path

        self.tabs: List[Template]

        dpg.create_viewport(title=self.default_title, width=1500, height=900)

        self.build_window()

        if self.replay_path is not None:
            self.open_replay(self.replay_path)

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def build_window(self):
        with dpg.window(tag="main_window"):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open", callback=lambda: self.open_replay(askopenfilename(defaultextension=".osr", filetypes=[("Osu! Replay", ".osr"), ("All files", "")], initialdir=CONFIG.osu_path + "\\Replays")))
                    dpg.add_menu_item(label="Save", callback=lambda: self.save_replay(self.replay_path))
                    dpg.add_menu_item(label="Save as...", callback=lambda: self.save_replay(asksaveasfilename(defaultextension=".osr", filetypes=[("Osu! Replay", ".osr"), ("All files", "")], initialdir=CONFIG.osu_path, initialfile="replay")))

            with dpg.tab_bar():
                self.tabs = [tab(self.on_update) for tab in tabs]

        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=400, height=150):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        dpg.set_primary_window("main_window", value=True)

    def on_update(self, *args, **kwargs):
        for tab in self.tabs:
            tab.read_in_replay(self.curr_replay)

        for tab in self.tabs:
            tab.update(self.osu_db, self.curr_replay)

    def save_replay(self, path=None):
        if self.curr_replay.game_version == 0:
            self.show_error("Please, open replay before saving")
            return
        if path is None:
            path = self.replay_path
        elif path == "":
            self.show_error("Please, select a file")
            return

        for tab in self.tabs:
            tab.read_in_replay(self.curr_replay)

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
            self.show_error(f"Error occured while trying to load replay: \n\n{e} \n\nPossibly, replay is corrupted")
            return
        self.replay_path = path
        self.curr_replay = replay

        for tab in self.tabs:
            tab.read_from_replay(self.curr_replay)

        for tab in self.tabs:
            tab.on_replay_load(self.osu_db, self.curr_replay)

        dpg.set_viewport_title(f"{self.default_title} {self.replay_path}")
