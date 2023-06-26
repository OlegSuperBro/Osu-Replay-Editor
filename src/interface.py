import PySimpleGUI as psg
import os
import sys
import pyperclip
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import ceil
from pyosudb import parse_osudb
from copy import deepcopy
from pathlib import Path
from datetime import datetime
from osrparse import Replay, Mod
from osrparse.utils import LifeBarState
from typing import Self

import utils
import calculation
from config import CONFIG


def generate_mods_checkboxes(width: int):
    mod_list = utils.mods_list()

    height = ceil(len(mod_list) / width)

    layout = []
    tmp_text_column = []
    tmp_checkbox_column = []

    mod_index = 0

    for _ in range(width):
        for _ in range(height):
            try:
                mod = mod_list[mod_index]
                mod_index += 1
            except IndexError:
                mod_index += 1
                continue

            tmp_text_column.append(psg.Text(mod, pad=((0, 0), (3, 7)), justification="right", size=(10, 1)))
            tmp_checkbox_column.append(psg.Checkbox("", key=f"-MOD_{mod.upper()}-"))

        tmp_column = psg.Column([[psg.Column([[text] for text in tmp_text_column]), psg.Column([[checkbox] for checkbox in tmp_checkbox_column])]])
        tmp_text_column = []
        tmp_checkbox_column = []
        layout.append(tmp_column)

    return [layout]


class TemplateWindow:
    LAYOUT = [[]]
    EVENT_FUNCS = {}

    WINDOW_NAME = "template"
    WINDOW_SIZE = ()
    WINDOW_TIMEOUT = 100

    def __init__(self) -> None:
        if len(self.WINDOW_SIZE) != 2:
            self.window = psg.Window(self.WINDOW_NAME, deepcopy(self.LAYOUT), finalize=True)
        else:
            self.window = psg.Window(self.WINDOW_NAME, deepcopy(self.LAYOUT), finalize=True, size=self.WINDOW_SIZE)

        self.EVENT_FUNCS = {}  # should be re-defined in __init__

    def main_loop(self) -> None:
        while True:
            self._loop_step()

    def _start(self) -> None:
        self.main_loop()

    def _loop_step(self) -> None:
        self.event, self.values = self.window.read(timeout=self.WINDOW_TIMEOUT)

        if self.event == psg.WIN_CLOSED or self.event == "-EXIT-":
            sys.exit(0)

        self.event = self.event.split("::")[-1:][0]  # bruh

        tmp_func = self.EVENT_FUNCS.get(self.event)
        if tmp_func is not None:
            tmp_func()

    def change_window(self, window: Self):
        self.window.close()
        del self
        window._start()

    @utils.run_async
    def open_window(self, window: Self):
        window._start()


class LifeGraphEditor(TemplateWindow):
    LAYOUT = [[psg.Canvas(key="-LIFE_GRAPH-", expand_x=True)]]

    WINDOW_NAME = "Replay Editor: Life Graph"
    WINDOW_SIZE = (1500, 400)
    WINDOW_TIMEOUT = 10

    def __init__(self, life_graph_data: list[LifeBarState]) -> None:
        super().__init__()

        self.life_graph_data = life_graph_data

        self.fig, self.axes = plt.subplots()

        self.line = Line2D([x.time for x in self.life_graph_data], [x.life * 100 for x in self.life_graph_data], marker="o", markeredgecolor="r", markersize=4)

        self.axes.add_line(self.line)

        # self.cid = self.poly.add_callback()

        # self.canvas.mpl_connect('draw_event', self.on_draw)
        # self.canvas.mpl_connect('button_press_event', self.on_button_press)
        # self.canvas.mpl_connect('key_press_event', self.on_key_press)
        # self.canvas.mpl_connect('button_release_event', self.on_button_release)
        # self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # self.canvas = canvas
        self.axes.set_xlim(0, self.life_graph_data[-1:][0].time)
        self.axes.set_ylim(0, 100)
        plt.xlabel('Ticks')
        plt.ylabel('%')
        plt.grid()

        figure_canvas_agg = FigureCanvasTkAgg(self.fig, master=self.window['-LIFE_GRAPH-'].TKCanvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

    def _loop_step(self) -> None:
        super()._loop_step()

        self.update_info()

    def update_info(self) -> None:
        pass


class ReplayEditor(TemplateWindow):
    WINDOW_NAME = "Replay Editor: Replay data"


class AttributesEditor(TemplateWindow):
    MENU_LAYOUT = [['&File', ['&Open::-OPEN_REPLAY-', '&Save::-SAVE-', '&Save As...::-SAVEAS-', '---', 'E&xit::-EXIT-']],
                   ['&Tools', ['&Life graph editor::-OPEN_LIFE_GRAPH_EDITOR-']]]

    CHANGING_TEXT_COL = psg.Column([[psg.Text("Player", pad=((0, 0), (0, 65)))],
                                    [psg.Text("300s")],
                                    [psg.Text("100s")],
                                    [psg.Text("50s")],
                                    [psg.Text("Gekis")],
                                    [psg.Text("Katus")],
                                    [psg.Text("Misses")],
                                    [psg.Text("Total score")],
                                    [psg.Text("Max combo")],
                                    [psg.Text("Perfect combo")],
                                    [psg.Text("Date")]])

    CHANGING_INPUT_COL = psg.Column([[psg.Multiline(default_text="", key="-USERNAME-", size=(50, 5)), psg.Text("", key="-USERNAME_ERROR-")],
                                     [psg.Input(default_text="0", key="-N300-", size=(12, 1)), psg.Text("", key="-N300_ERROR-")],
                                     [psg.Input(default_text="0", key="-N100-", size=(12, 1)), psg.Text("", key="-N100_ERROR-")],
                                     [psg.Input(default_text="0", key="-N50-", size=(12, 1)), psg.Text("", key="-N50_ERROR-")],
                                     [psg.Input(default_text="0", key="-NGEKIS-", size=(12, 1)), psg.Text("", key="-NGEKIS_ERROR-")],
                                     [psg.Input(default_text="0", key="-NKATUS-", size=(12, 1)), psg.Text("", key="-NKATUS_ERROR-")],
                                     [psg.Input(default_text="0", key="-NMISSES-", size=(12, 1)), psg.Text("", key="-NMISSES_ERROR-")],
                                     [psg.Input(default_text="0", key="-TOTAL_SCORE-", size=(12, 1)), psg.Text("", key="-TOTAL_SCORE_ERROR-")],
                                     [psg.Input(default_text="0", key="-MAX_COMBO-", size=(12, 1)), psg.Text("", key="-MAX_COMBO_ERROR-")],
                                     [psg.Checkbox("", key="-PFC-",)],

                                     [psg.CalendarButton("", key="-TIMESTAMP_DATE-", target=(psg.ThisRow, 0), close_when_date_chosen=False, format="%d/%m/%Y"),
                                     psg.Spin(list(range(0, 24)), key="-TIMESTAMP_HOUR-", initial_value=datetime.today().strftime("%H")[:1], size=(2, 1)),
                                     psg.Spin(list(range(0, 60)), key="-TIMESTAMP_MINUTE-", initial_value=datetime.today().strftime("%M"), size=(2, 1)),
                                     psg.Spin(list(range(0, 60)), key="-TIMESTAMP_SECOND-", initial_value=datetime.today().strftime("%S"), size=(2, 1))]])

    CHANGING_COL = psg.Column([[CHANGING_TEXT_COL, CHANGING_INPUT_COL],
                               [psg.Frame("Mods", generate_mods_checkboxes(5))]])

    INFO_COL = psg.Column([[psg.Text("Beatmap: "), psg.Text("None", key="-INFO_BEATMAP-")],
                           [psg.Text("Total accuracy: "), psg.Text("None", key="-INFO_ACCURACY-")],
                           [psg.Text("Total PP: "), psg.Text("None", key="-INFO_PP-")]],
                          expand_y=True)

    MAIN_COL = psg.Column([[CHANGING_COL, INFO_COL]])

    LAYOUT = [[psg.Menu(MENU_LAYOUT)],
              [MAIN_COL],
              [psg.Text("CLI command")],
              [psg.InputText(key="-CLI_COMMAND-", readonly=True, expand_x=True), psg.Button("Copy", key="-COPY_CLI-")]]

    WINDOW_NAME = "Replay Editor: Attributes"

    WINDOW_TIMEOUT = 10

    def __init__(self) -> None:
        super().__init__()

        self.osu_db = parse_osudb(Path(CONFIG.get("osu_path")) / "osu!.db")
        self.replay_path = None
        self.replay = None

        self.EVENT_FUNCS = {
            "-OPEN_REPLAY-": lambda: self.open_replay(),
            "-SAVE-": lambda: self.save_replay(),
            "-SAVEAS-": lambda: self.save_as_replay(),
            "-COPY_CLI-": lambda: self.clipboard_copy_CLI_command(),
            "-OPEN_LIFE_GRAPH_EDITOR-": lambda: self.open_life_graph_editor(),
            }

    def _loop_step(self) -> None:
        super()._loop_step()

        self.update_info()

    def check_info(self):
        for value_name, value_of_value in self.values.items():
            value_correct, value_limit = utils.check_limit(value_name, value_of_value)
            if not value_correct:
                self.show_wrong_range(value_name, f"NOT IN {value_limit}")
                return False
            else:
                self.hide_wrong_range(value_name)
        return True

    def update_info(self):
        if not self.check_info():
            return False

        n300, n100, n50, nmiss, n_geki, n_katu, max_combo = int(self.values["-N300-"]), int(self.values["-N100-"]), int(self.values["-N50-"]), int(self.values["-NMISSES-"]), int(self.values["-NGEKIS-"]), int(self.values["-NKATUS-"]), int(self.values["-MAX_COMBO-"])

        acc = calculation.calculate_acc(n300, n100, n50, nmiss)
        self.window["-INFO_ACCURACY-"].update(f"{str(acc)}%")

        if self.replay is not None:
            beatmap = self.osu_db.get_beatmap_from_hash(self.replay.beatmap_hash)
            beatmap_path = str(Path(CONFIG.get("osu_path")) / "songs" / beatmap.folder_name / beatmap.osu_file)
            pp = calculation.calculate_pp(beatmap_path, mode=self.replay.mode, mods=self.get_mods(), n_geki=n_geki, n_katu=n_katu, n300=n300, n100=n100, n50=n50, n_misses=nmiss, combo=max_combo)

            self.window["-INFO_PP-"].update(f"{str(pp)}pp")

        self.window["-CLI_COMMAND-"].update(self.generate_CLI_command())

        if self.replay is not None and self.values["-TIMESTAMP_DATE-"] == "":
            self.values["-TIMESTAMP_DATE-"] = self.replay.timestamp.strftime("%d/%m/%Y")
        elif self.values["-TIMESTAMP_DATE-"] == "":
            self.values["-TIMESTAMP_DATE-"] = datetime.today().strftime("%d/%m/%Y")

        self.window["-TIMESTAMP_DATE-"].update(self.values["-TIMESTAMP_DATE-"])

        return True

    def show_error(self, error_msg):
        psg.popup(error_msg, title="ERROR")

    def show_wrong_range(self, value_key: str, message: str):
        self.window.find_element(f"-{value_key.replace('-', '')}_ERROR-", silent_on_error=True).update(message)

    def hide_wrong_range(self, value_key: str):
        try:
            elem = self.window.find_element(f"-{value_key.replace('-', '')}_ERROR-", silent_on_error=True)
            if not hasattr(self, "window_elements"):
                self.window_elements = self.window.element_list()
            if elem in self.window_elements:
                elem.update("")
        except AttributeError:
            pass

    def generate_CLI_command(self, output_path: str = "[output]"):
        if self.replay is not None and self.values["-TIMESTAMP_DATE-"] == "":
            self.values["-TIMESTAMP_DATE-"] = self.replay.timestamp.strftime("%d/%m/%Y")
        elif self.values["-TIMESTAMP_DATE-"] == "":
            self.values["-TIMESTAMP_DATE-"] = datetime.today().strftime("%d/%m/%Y")

        date = datetime.strptime(f"{self.values['-TIMESTAMP_DATE-']} {self.values['-TIMESTAMP_HOUR-']}:{self.values['-TIMESTAMP_MINUTE-']}:{self.values['-TIMESTAMP_SECOND-']}", "%d/%m/%Y %H:%M:%S")

        return utils.generate_command(self.replay_path,
                                      self.values["-USERNAME-"], self.values["-N300-"], self.values["-N100-"], self.values["-N50-"],
                                      self.values["-NGEKIS-"], self.values["-NKATUS-"], self.values["-NMISSES-"], self.values["-TOTAL_SCORE-"],
                                      self.values["-MAX_COMBO-"], self.values["-PFC-"], None, self.get_mods(), utils.date2windows_ticks(date), output_path)

    def clipboard_copy_CLI_command(self):
        pyperclip.copy(self.generate_CLI_command())

    def get_mods(self):
        mods = []
        for mod in utils.mods_list():
            if self.values[f"-MOD_{mod.upper()}-"] is True:
                mods.append(mod)
        return Mod(utils.mods2code(mods))

    def save_replay(self):
        if not self.check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        os.system(self.generate_CLI_command(self.replay_path, self.replay_path))

    def save_as_replay(self):
        if not self.check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        path = psg.popup_get_file("Save as...", save_as=True, no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            os.system(self.generate_CLI_command(self.replay_path, path))

    def open_replay(self):
        path = psg.popup_get_file("Open file...", no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            self.replay_path = path
            self.replay = Replay.from_path(path)

            self.window["-USERNAME-"].update(f"{self.replay.username}")
            self.window["-N300-"].update(f"{self.replay.count_300}")
            self.window["-N100-"].update(f"{self.replay.count_100}")
            self.window["-N50-"].update(f"{self.replay.count_50}")
            self.window["-NGEKIS-"].update(f"{self.replay.count_geki}")
            self.window["-NKATUS-"].update(f"{self.replay.count_katu}")
            self.window["-NMISSES-"].update(f"{self.replay.count_miss}")
            self.window["-TOTAL_SCORE-"].update(f"{self.replay.score}")
            self.window["-MAX_COMBO-"].update(f"{self.replay.max_combo}")
            self.window["-PFC-"].update(self.replay.perfect)

            self.values["-TIMESTAMP_HOUR-"] = self.replay.timestamp.strftime("%H")
            self.values["-TIMESTAMP_MINUTE-"] = self.replay.timestamp.strftime("%M")
            self.values["-TIMESTAMP_SECOND-"] = self.replay.timestamp.strftime("%S")

            beatmap = self.osu_db.get_beatmap_from_hash(self.replay.beatmap_hash)
            self.window["-INFO_BEATMAP-"].update(f"{beatmap.artist} // {beatmap.mapper} - {beatmap.title}")

            for mod in utils.mods_list():
                self.window[f"-MOD_{mod.upper()}-"].update(True if Mod(utils.mods2code([mod])) in self.replay.mods else False)

    def open_life_graph_editor(self):
        if self.replay is None:
            self.show_error("Please, open replay first")
            return

        self.open_window(LifeGraphEditor(self.replay.life_bar_graph))


if __name__ == "__main__":
    app = AttributesEditor()

    app._start()
