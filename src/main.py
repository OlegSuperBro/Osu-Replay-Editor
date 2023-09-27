import dearpygui.dearpygui as dpg
import DearPyGui_DragAndDrop as dpg_dnd
import contextlib
import sys
import traceback
import asyncio
from datetime import datetime

from config import save as save_config, CONSTANTS, CONFIG

if "__compiled__" in locals():
    sys.path.append(CONSTANTS.PATHS.program_path + "/lib/site-packages/")

from lib.plugin import runner
from interface import MainWindow, StartupWindow
from app_globals import app_globals, init_globals


if __name__ == "__main__":
    try:
        # first we run welcome/startup window
        dpg.create_context()
        dpg.create_viewport()

        dpg.setup_dearpygui()
        dpg.show_viewport()

        win = StartupWindow()
        dpg.configure_viewport(0, title=win.default_title, width=350, height=500, resizable=False)

        app_update_avalable = False
        if not CONFIG.app_ignore_updates:
            loop = asyncio.get_event_loop()

            tasks = asyncio.wait([loop.create_task(win.app_check_for_update(), name="update"),
                                  loop.create_task(win.app_cycle_update_text()),
                                  loop.create_task(win.update_frame(), name="render")],
                                 return_when=asyncio.FIRST_COMPLETED)
            result, _ = loop.run_until_complete(tasks)

            for task in result:
                if task.get_name() == "render":
                    sys.exit()

                elif task.get_name() == "update":
                    app_update_avalable = task.result()

        if not CONFIG.app_ignore_updates:
            loop = asyncio.get_event_loop()
            tasks = asyncio.wait([loop.create_task(win.plugin_check_for_requirements(), name="install_requirements"),
                                  loop.create_task(win.app_cycle_update_text()),
                                  loop.create_task(win.update_frame(), name="render")],
                                 return_when=asyncio.FIRST_COMPLETED)
            result, _ = loop.run_until_complete(tasks)

            for task in result:
                if task.get_name() == "render":
                    sys.exit()

                elif task.get_name() == "install_requirements":
                    pass

        while dpg.is_dearpygui_running() and win.running and (app_update_avalable):
            dpg.render_dearpygui_frame()

        if not dpg.is_dearpygui_running():
            sys.exit()

        init_globals()

        #  clean up all items before starting main window
        #  this required cuz creating another viewport is pain
        for item in dpg.get_all_items():
            with contextlib.suppress(SystemError):
                dpg.delete_item(item)
        runner.run_funcs(app_globals.plugin_funcs.on_start)

        dpg_dnd.initialize()
        win = MainWindow()
        dpg.configure_viewport(0, title=win.default_title, width=1500, height=900)

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
