import dearpygui.dearpygui as dpg
import sys
import traceback

from gui import MainWindow
from CLI import CLI_run

if __name__ == "__main__":
    if len(sys.argv) > 1:
        CLI_run()
    else:
        try:
            MainWindow()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            traceback.print_exc()
        finally:
            # dpg.save_init_file("dpg.ini")
            pass
