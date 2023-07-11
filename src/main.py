import dearpygui.dearpygui as dpg
import sys

from interface import MainWindow
from CLI import CLI_run

if __name__ == "__main__":
    if len(sys.argv) > 1:
        CLI_run()
    else:
        try:
            MainWindow()
        except Exception as e:
            print(e)
        finally:
            dpg.save_init_file("dpg.ini")
