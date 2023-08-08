import dearpygui.dearpygui as dpg
import sys
import traceback
from osrparse import Replay
from datetime import datetime

from interface import MainWindow
from app_globals import app_globals, init_globals
from lib.plugin.runner import run_funcs

if __name__ == "__main__":
    init_globals()

    run_funcs(app_globals.plugin_funcs.on_start)

    try:
        dpg.create_context()
        win = MainWindow()

        try:
            if len(sys.argv) > 1:
                app_globals.replay = Replay.from_path(sys.argv[1])
                app_globals.replay_path = sys.argv[1]
                run_funcs(app_globals.plugin_funcs.on_replay_load)

        except TypeError:
            pass
        except Exception:
            win.show_error(f"Error occured while trying to load replay: \n\n{traceback.format_exc()} \n\nPossibly, replay is corrupted or path is incorrect")

        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        with open("traceback.txt", "w") as f:
            f.write(datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n")
            f.write(traceback.format_exc())
