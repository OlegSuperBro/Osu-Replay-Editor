import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
import asyncio
import webbrowser
from filedialogs import open_file_dialog, save_file_dialog

from config import CONFIG, CONSTANTS
from app_globals import app_globals
from lib.plugin.runner import run_funcs
from updater import app_check_update
from replay_controller import open_replay, save_replay
from lib.errors import CorruptedReplayError, NotSupportedExtentionError, EmptyReplayError, EmptyPathError


class MainWindow:
    default_title = "Replay Editor"

    def __init__(self) -> None:
        app_globals.data_update_func = self.on_data_update
        self.build()

        dpg_dnd.set_drop(lambda x, _: self.show_error("Sorry, but curentlry drag'n'drop don't supported for multiple files") if len(x) != 1 else self.open_replay(x[0]))

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
        try:
            save_replay(app_globals.replay_path if save_on_replay_path else path)

        except EmptyReplayError:
            self.show_error("Please, open replay before saving")

        except EmptyPathError:
            self.show_error("Please, select a file")

        dpg.set_viewport_title(f"{self.default_title} {app_globals.replay_path}")

    def on_data_update(self, *args):  # why caller passed only on build :(  i hate this
        run_funcs(app_globals.plugin_funcs.on_data_update)

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)

    def open_replay(self, path: str):
        try:
            open_replay(path)
        except NotSupportedExtentionError:
            self.show_error("Files with this extension is not supported")
            return

        except CorruptedReplayError:
            self.show_error("Error occured while trying to load replay. \nPossibly, replay is corrupted")
            return

        dpg.set_viewport_title(f"{self.default_title} {app_globals.replay_path}")


class StartupWindow:
    default_title = "Replay Editor"

    def __init__(self) -> None:
        self.running = True
        self.build()

    def build(self):
        def disable_update_checks():
            CONFIG.app_ignore_updates = True

        def stop_running():
            self.running = False

        with dpg.window(label="Error", modal=True, show=False, tag="error_popup", no_resize=True, width=100, height=200):
            dpg.add_text("", tag="error_text")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("error_popup", show=False))

        with dpg.window(tag=CONSTANTS.TAGS.startup_window):
            #  checks update for app
            with dpg.group(tag="app_checking_update"):
                dpg.add_text("Checking for updates", tag="checking_updates")
            #  shows update is available
            with dpg.group(tag="app_showing_update", show=False):
                dpg.add_text("App update is avalable")
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Ignore", callback=lambda: dpg.hide_item("app_showing_update"))
                        dpg.add_button(label="Go to download page", callback=lambda: webbrowser.open("https://github.com/OlegSuperBro/Osu-Replay-Editor/releases/latest"))
                    dpg.add_button(label="Never check updates", callback=lambda: disable_update_checks())

            #  cheking plugins updates
            with dpg.group(tag="plugin_checking_update"):
                pass
            #  updating them
            with dpg.group(tag="plugin_showing_update"):
                pass

            dpg.add_button(label="Continue", callback=lambda: stop_running())

        dpg.set_primary_window(CONSTANTS.TAGS.startup_window, value=True)

    async def app_check_for_update(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, app_check_update)

    async def app_cycle_update_text(self):
        check_for_update_state = 0
        while True:
            if check_for_update_state > 3:
                check_for_update_state = 0

            dpg.configure_item("checking_updates", default_value="Checking for updates" + "." * check_for_update_state)

            check_for_update_state += 1
            await asyncio.sleep(0.5)

    async def update_frame(self):
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            await asyncio.sleep(0)

    def show_error(self, error_text):
        dpg.set_value("error_text", error_text)
        dpg.set_item_pos("error_popup", ((dpg.get_viewport_client_width() - dpg.get_item_width("error_popup")) / 2, (dpg.get_viewport_height() - dpg.get_item_height("error_popup")) / 2))
        dpg.configure_item("error_popup", show=True)

    def show_app_update_avalable(self):
        dpg.hide_item("app_checking_update")
        dpg.show_item("app_showing_update")
