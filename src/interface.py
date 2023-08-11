import dearpygui.dearpygui as dpg
from osrparse import Replay
from filedialogs import open_file_dialog, save_file_dialog

from config import CONFIG, CONSTANTS
from app_globals import app_globals
from lib.plugin.runner import run_funcs


class MainWindow:
    default_title = "Replay Editor"

    def __init__(self) -> None:
        dpg.create_viewport(title=self.default_title, width=1500, height=900)

        app_globals.data_update_func = self.on_data_update
        self.build()

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def build(self):
        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=500, height=300):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        self.build_window()

    def build_window(self):
        if dpg.does_item_exist(CONSTANTS.TAGS.main_window):
            dpg.delete_item(CONSTANTS.TAGS.main_window)

        with dpg.window(tag=CONSTANTS.TAGS.main_window):
            with dpg.menu_bar(tag=CONSTANTS.TAGS.menu_bar):
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open", callback=lambda: self.open_replay(open_file_dialog(title="Open...", directory=CONFIG.osu_path + "\\Replays", default_ext="osr", ext=[("Osu! Replay (*.osr)", "osr"), ("All files (*.*)", "*")])))
                    dpg.add_menu_item(label="Save", callback=lambda: self.save_replay(app_globals.replay_path, True))
                    dpg.add_menu_item(label="Save as...", callback=lambda: self.save_replay(save_file_dialog(title="Save as...", directory=CONFIG.osu_path, default_name="replay", default_ext="osr", ext=[("Osu! Replay (*.osr)", "osr"), ("All files (*.*)", "*")])))

            dpg.add_tab_bar(tag=CONSTANTS.TAGS.tab_bar)

        dpg.set_primary_window(CONSTANTS.TAGS.main_window, value=True)

        run_funcs(app_globals.plugin_funcs.on_window_build)

    def save_replay(self, path=None, save_on_replay_path: bool = False):
        if app_globals.replay.game_version == 0:
            self.show_error("Please, open replay before saving")
            return
        if save_on_replay_path:
            path = app_globals.replay_path
        elif path == "" or path is None:
            self.show_error("Please, select a file")
            return

        run_funcs(app_globals.plugin_funcs.on_replay_save)

        app_globals.replay.write_path(path)

        app_globals.replay_path = path
        dpg.set_viewport_title(f"{self.default_title} {app_globals.replay_path}")

    def on_data_update(self, *args):  # why caller passed only on build :(  i hate this
        run_funcs(app_globals.plugin_funcs.on_data_update)

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)

    def open_replay(self, path):
        if path == "" or path is None:
            return
        try:
            replay = Replay.from_path(path)
        except Exception as e:
            self.show_error(f"Error occured while trying to load replay: \n\n{e} \n\nPossibly, replay is corrupted")
            return
        app_globals.replay_path = path
        app_globals.replay = replay

        run_funcs(app_globals.plugin_funcs.on_replay_load)

        dpg.set_viewport_title(f"{self.default_title} {app_globals.replay_path}")


class StartupWindow:
    default_title = "Replay Editor"

    def __init__(self) -> None:
        dpg.create_viewport(title=self.default_title, width=1500, height=900)

        self.build()

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def build(self):
        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=500, height=300):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        self.build_window()

    def build_window(self):

        with dpg.window(tag=CONSTANTS.TAGS.startup_window):
            dpg.add_text("pass")

        dpg.set_primary_window(CONSTANTS.TAGS.startup_window, value=True)

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)
