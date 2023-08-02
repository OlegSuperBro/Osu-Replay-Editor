import dearpygui.dearpygui as dpg
import sys
import traceback
from osrparse import Replay, GameMode, Mod
from datetime import datetime

from gui.main_window import MainWindow

DEFAULT_REPLAY = Replay(GameMode(0), 0, "", "", "", 0, 0, 0, 0, 0, 0, 0, 0, False, Mod(0), [], datetime.now(), [], 0, None)
if __name__ == "__main__":
    error = None
    replay = None
    replay_path = None
    try:
        replay = Replay.from_path(sys.argv[1] if len(sys.argv) > 1 else None)
        replay_path = sys.argv[1] if len(sys.argv) > 1 else None
    except TypeError:
        pass
    except Exception:
        error = f"Error occured while trying to load replay: \n\n{traceback.format_exc()} \n\nPossibly, replay is corrupted or path is incorrect"
        replay = DEFAULT_REPLAY
        replay_path = None

    try:
        dpg.create_context()
        win = MainWindow(replay, replay_path)
        if error:
            win.show_error(error)
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            win.on_update()
        dpg.destroy_context()

    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        with open("traceback.txt", "w") as f:
            f.write(datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n")
            f.write(traceback.format_exc())
