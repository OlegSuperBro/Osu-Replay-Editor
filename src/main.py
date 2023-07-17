import dearpygui.dearpygui as dpg
import sys
import traceback

from gui import MainWindow

if __name__ == "__main__":
    try:
        MainWindow(sys.argv[1] if len(sys.argv) > 1 else None)
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        input("Press ENTER to continue")
    finally:
        dpg.save_init_file("dpg.ini")
