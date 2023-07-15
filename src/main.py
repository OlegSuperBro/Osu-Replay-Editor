import dearpygui.dearpygui as dpg
import sys
import traceback

from gui import MainWindow
from CLI import CLI_run

if __name__ == "__main__":
    if len(sys.argv) > 2:
        CLI_run()
    else:
        try:
            MainWindow(sys.argv[1] if len(sys.argv) > 1 else None)
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            input("Press ENTER to continue")
        finally:
            dpg.save_init_file("dpg.ini")
