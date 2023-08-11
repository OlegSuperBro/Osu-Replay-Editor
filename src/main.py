import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
import sys
import traceback
from datetime import datetime

from config import save as save_config, CONSTANTS

if "__compiled__" in locals():
    sys.path.append(CONSTANTS.PATHS.program_path + "/lib/site-packages/")

from lib.plugin import runner
from interface import MainWindow
from app_globals import app_globals, init_globals

if __name__ == "__main__":
    try:
        init_globals()
        runner.run_funcs(app_globals.plugin_funcs.on_start)

        dpg.create_context()
        dpg_dnd.initialize()
        win = MainWindow()

        if len(sys.argv) > 1:
            dpg.render_dearpygui_frame()
            win.open_replay(sys.argv[1])

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
    finally:
        save_config()
