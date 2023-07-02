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
            tmp_checkbox_column.append(psg.Checkbox("", key=f"-ATTR_MOD_{mod.upper()}-", metadata=Mod[mod], enable_events=True))

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

    def _loop_step(self, timeout: int = WINDOW_TIMEOUT) -> None:
        self.event, self.values = self.window.read(timeout=timeout)

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

    def show_error(self, error_msg):
        psg.popup(error_msg, title="ERROR")


class MainWindow(TemplateWindow):
    WINDOW_NAME = "Replay Editor"
    WINDOW_SIZE = (1200, 700)
    WINDOW_TIMEOUT = None

    TOOLBAR_LAYOUT = [['&File', ['&Open::-OPEN_REPLAY-', '&Save::-SAVE-', '&Save As...::-SAVEAS-', '---', 'E&xit::-EXIT-']]]

    MENU_LAYOUT = [[psg.Column([[]], size=(50, 0))],  # TODO maybe add logo or drag'n'drop?
                   [psg.Button("Attributes", key="-SWITCH_ATTR-", expand_x=True)],
                   [psg.Button("Life Graph", key="-SWITCH_LIFE-", expand_x=True)],
                   [psg.Button("Replay data (WIP)", key="-SWITCH_DATA-", expand_x=True)]]

    ATTR_TEXT_COL = psg.Column([[psg.Text("Player", pad=((0, 0), (0, 65)), justification="right", expand_x=True)],
                                [psg.Text("300s", justification="right", expand_x=True)],
                                [psg.Text("100s", justification="right", expand_x=True)],
                                [psg.Text("50s", justification="right", expand_x=True)],
                                [psg.Text("Gekis", justification="right", expand_x=True)],
                                [psg.Text("Katus", justification="right", expand_x=True)],
                                [psg.Text("Misses", justification="right", expand_x=True)],
                                [psg.Text("Total score", justification="right", expand_x=True)],
                                [psg.Text("Max combo", justification="right", expand_x=True)],
                                [psg.Text("Perfect combo", justification="right", expand_x=True)],
                                [psg.Text("Date", pad=((0, 0), (10, 0)), justification="right", expand_x=True)]])

    ATTR_INPUT_COL = psg.Column([[psg.Multiline(default_text="", key="-ATTR_USERNAME-", size=(50, 5), enable_events=True), psg.Text("", key="-USERNAME_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_N300-", size=(12, 1), enable_events=True), psg.Text("", key="-N300_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_N100-", size=(12, 1), enable_events=True), psg.Text("", key="-N100_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_N50-", size=(12, 1), enable_events=True), psg.Text("", key="-N50_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_NGEKIS-", size=(12, 1), enable_events=True), psg.Text("", key="-NGEKIS_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_NKATUS-", size=(12, 1), enable_events=True), psg.Text("", key="-NKATUS_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_NMISSES-", size=(12, 1), enable_events=True), psg.Text("", key="-NMISSES_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_TOTAL_SCORE-", size=(12, 1), enable_events=True), psg.Text("", key="-TOTAL_SCORE_ERROR-")],
                                 [psg.Input(default_text="0", key="-ATTR_MAX_COMBO-", size=(12, 1), enable_events=True), psg.Text("", key="-MAX_COMBO_ERROR-")],
                                 [psg.Checkbox("", key="-PFC-", enable_events=True)],

                                 [psg.CalendarButton("", key="-ATTR_TIMESTAMP_DATE-", target=(psg.ThisRow, 0), close_when_date_chosen=False, format="%d/%m/%Y", enable_events=True),
                                 psg.Spin(list(range(0, 24)), key="-ATTR_TIMESTAMP_HOUR-", initial_value=datetime.today().strftime("%H"), size=(2, 1), enable_events=True),
                                 psg.Spin(list(range(0, 60)), key="-ATTR_TIMESTAMP_MINUTE-", initial_value=datetime.today().strftime("%M"), size=(2, 1), enable_events=True),
                                 psg.Spin(list(range(0, 60)), key="-ATTR_TIMESTAMP_SECOND-", initial_value=datetime.today().strftime("%S"), size=(2, 1), enable_events=True)]])

    ATTRIBUTES_LAYOUT = [[psg.Column([[ATTR_TEXT_COL, ATTR_INPUT_COL],
                         [psg.Frame("Mods", generate_mods_checkboxes(5))]])]]
    LIFE_GRAPH_LAYOUT = [[psg.Canvas(key="-LIFE_GRAPH-", expand_x=True, expand_y=False)]]
    REPLAY_DATA_LAYOUT = [[]]

    EDITING_COLUMN = psg.Column([[psg.Column(ATTRIBUTES_LAYOUT, key="-ATTR-"), psg.Column(LIFE_GRAPH_LAYOUT, visible=False, key="-LIFE-"), psg.Column(REPLAY_DATA_LAYOUT, visible=False, key="-DATA-")]])

    INFO_COL = psg.Column([[psg.Text("Beatmap: "), psg.Text("None", key="-INFO_BEATMAP-")],
                           [psg.Text("Total accuracy: "), psg.Text("None", key="-INFO_ACCURACY-")],
                           [psg.Text("Total PP: "), psg.Text("None", key="-INFO_PP-")],
                           [psg.VPush()]],
                          expand_y=True)

    LAYOUT = [[psg.Menu(TOOLBAR_LAYOUT)],
              [psg.Column(MENU_LAYOUT, size=(200, WINDOW_SIZE[1])), psg.Column([[EDITING_COLUMN, INFO_COL],
                                                                                [psg.VPush()],
                                                                                [psg.InputText(key="-CLI_COMMAND-", readonly=True, expand_x=True), psg.Button("Copy", key="-COPY_CLI-")]], expand_x=True, expand_y=True)]]

    current_layout = "-ATTR-"

    EPSILON = 5

    def __init__(self) -> None:
        super().__init__()

        self.osu_db = parse_osudb(Path(CONFIG.get("osu_path")) / "osu!.db")
        # self.osu_db = None
        self.replay_path = None
        self.replay = None

        self.EVENT_FUNCS = {
            "-OPEN_REPLAY-": lambda: self.open_replay(),
            "-SAVE-": lambda: self.save_replay(),
            "-SAVEAS-": lambda: self.save_as_replay(),
            "-COPY_CLI-": lambda: self.clipboard_copy_CLI_command(),
            "-SWITCH_ATTR-": lambda: self.switch_layout("-ATTR-"),
            "-SWITCH_LIFE-": lambda: self.switch_layout("-LIFE-"),
            # "-SWITCH_DATA-": lambda: self.switch_layout("-DATA-"),  # TODO uncomment when data editing is done
            }

        self.attr_init()
        self.life_init()

        self._loop_step(1)

    def _loop_step(self, timeout: int = WINDOW_TIMEOUT):
        super()._loop_step(timeout)

        self.update_info()

    # ------------------------ATTRIBUTES------------------------ #
    def attr_init(self):
        pass

    def attr_show_wrong_range(self, value_key: str, message: str):
        self.window.find_element(f"-{value_key.replace('-', '')}_ERROR-", silent_on_error=True).update(message)

    def attr_check_info(self):
        for value_name, value_of_value in self.values.items():
            value_correct, value_limit = utils.check_limit(value_name, value_of_value)
            if not value_correct:
                self.attr_show_wrong_range(value_name, f"NOT IN {value_limit}")
                return False
            else:
                self.attr_hide_wrong_range(value_name)
        return True

    def attr_hide_wrong_range(self, value_key: str):
        try:
            elem = self.window.find_element(f"-{value_key.replace('-', '')}_ERROR-", silent_on_error=True)
            if not hasattr(self, "window_elements"):
                self.window_elements = self.window.element_list()
            if elem in self.window_elements:
                elem.update("")
        except AttributeError:
            pass

    def attr_get_mods(self):
        mods = []
        for mod in utils.mods_list():
            if self.values[f"-ATTR_MOD_{mod.upper()}-"] is True:
                mods.append(mod)
        return Mod(utils.mods2code(mods))

    # ------------------------LIFE GRAPH------------------------ #

    def life_init(self):
        try:
            self.life_graph_data = ([x.time for x in self.replay.life_bar_graph], [x.life * 100 for x in self.replay.life_bar_graph])
        except AttributeError:
            self.life_graph_data = ([0], [0])

        self.fig, self.life_axes = plt.subplots()

        self.life_line = Line2D(*self.life_graph_data, marker="o", markeredgecolor="r", markersize=4, animated=True)

        self.life_axes.add_line(self.life_line)

        self.canvas = self.life_line.get_figure().canvas

        self.life_line.get_figure().canvas.mpl_connect('draw_event', self.life_on_draw)
        self.life_line.get_figure().canvas.mpl_connect('button_press_event', self.life_on_button_press)
        self.life_line.get_figure().canvas.mpl_connect('button_release_event', self.life_on_button_release)
        self.life_line.get_figure().canvas.mpl_connect('motion_notify_event', self.life_on_mouse_move)

        self.life_axes.set_xlim(0, self.life_graph_data[0][-1:][0])
        self.life_axes.set_ylim(0, 100)
        plt.xlabel('Ticks')
        plt.ylabel('%')
        plt.grid()

        figure_canvas_agg = FigureCanvasTkAgg(self.fig, master=self.window['-LIFE_GRAPH-'].TKCanvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='left', fill='both', expand=1)

        self.life_cur_index = None

    def life_get_ind_under_point(self, event):
        """
        Return the index of the point closest to the event position or *None*
        if no point is within ``self.EPSILON`` to the event position.
        """
        xy = np.asarray(self.life_line.get_xydata())
        xyt = self.life_line.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.hypot(xt - event.x, yt - event.y)
        indseq, = np.nonzero(d == d.min())
        ind = indseq[0]

        if d[ind] >= self.EPSILON:
            ind = None

        return ind

    def life_on_draw(self, event):
        self.background = self.life_line.get_figure().canvas.copy_from_bbox(self.life_axes.bbox)
        self.life_axes.draw_artist(self.life_line)

    def life_on_button_press(self, event):
        """Callback for mouse button presses."""
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self.life_cur_index = self.life_get_ind_under_point(event)

    def life_on_button_release(self, event):
        """Callback for mouse button releases."""
        if event.button != 1:
            return
        self.life_cur_index = None

    def life_on_mouse_move(self, event):
        if self.life_cur_index is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata

        if self.life_cur_index < len(self.life_graph_data[0]) and x <= self.life_graph_data[0][self.life_cur_index - 1]:
            x = self.life_graph_data[0][self.life_cur_index - 1]
        if self.life_cur_index > 0 and x >= self.life_graph_data[0][self.life_cur_index + 1]:
            x = self.life_graph_data[0][self.life_cur_index + 1]

        if y >= 100:
            y = 100
        if y <= 0:
            y = 0

        self.life_graph_data[0][self.life_cur_index], self.life_graph_data[1][self.life_cur_index] = int(x), y
        if self.life_cur_index == 0:
            self.life_graph_data[0][-1], self.life_graph_data[1][-1] = int(x), y
        elif self.life_cur_index == len(list(zip(*self.life_graph_data))) - 1:
            self.life_graph_data[0][0], self.life_graph_data[1][0] = int(x), y

        self.life_update_graph()

    def life_update_graph(self):
        self.life_line.set_data(self.life_graph_data)

        self.life_line.get_figure().canvas.restore_region(self.background)
        self.life_axes.draw_artist(self.life_line)
        self.life_line.get_figure().canvas.blit(self.life_axes.bbox)

    # ---------------------------OTHER--------------------------- #
    def generate_CLI_command(self, output_path: str = "[output]"):
        if self.replay is not None and self.values["-ATTR_TIMESTAMP_DATE-"] == "":
            self.values["-ATTR_TIMESTAMP_DATE-"] = self.replay.timestamp.strftime("%d/%m/%Y")
        elif self.values["-ATTR_TIMESTAMP_DATE-"] == "":
            self.values["-ATTR_TIMESTAMP_DATE-"] = datetime.today().strftime("%d/%m/%Y")

        date = datetime.strptime(f"{self.values['-ATTR_TIMESTAMP_DATE-']} {self.values['-ATTR_TIMESTAMP_HOUR-']}:{self.values['-ATTR_TIMESTAMP_MINUTE-']}:{self.values['-ATTR_TIMESTAMP_SECOND-']}", "%d/%m/%Y %H:%M:%S")
        return utils.generate_command(self.replay_path,
                                      self.values["-ATTR_USERNAME-"], self.values["-ATTR_N300-"], self.values["-ATTR_N100-"], self.values["-ATTR_N50-"],
                                      self.values["-ATTR_NGEKIS-"], self.values["-ATTR_NKATUS-"], self.values["-ATTR_NMISSES-"], self.values["-ATTR_TOTAL_SCORE-"],
                                      self.values["-ATTR_MAX_COMBO-"], self.values["-PFC-"], None, self.attr_get_mods(), utils.date2windows_ticks(date), utils.lifebar2str([LifeBarState(int(time), life) for time, life in zip(*self.life_graph_data)]) if self.replay is not None else None, output_path)

    def clipboard_copy_CLI_command(self):
        pyperclip.copy(self.generate_CLI_command())

    def update_info(self):
        if not self.attr_check_info():
            return False

        n300, n100, n50, nmiss, n_geki, n_katu, max_combo = int(self.values["-ATTR_N300-"]), int(self.values["-ATTR_N100-"]), int(self.values["-ATTR_N50-"]), int(self.values["-ATTR_NMISSES-"]), int(self.values["-ATTR_NGEKIS-"]), int(self.values["-ATTR_NKATUS-"]), int(self.values["-ATTR_MAX_COMBO-"])

        acc = calculation.calculate_acc(n300, n100, n50, nmiss)
        self.window["-INFO_ACCURACY-"].update(f"{str(acc)}%")

        if self.replay is not None:
            beatmap = self.osu_db.get_beatmap_from_hash(self.replay.beatmap_hash)
            beatmap_path = str(Path(CONFIG.get("osu_path")) / "songs" / beatmap.folder_name / beatmap.osu_file)
            pp = calculation.calculate_pp(beatmap_path, mode=self.replay.mode, mods=self.attr_get_mods(), n_geki=n_geki, n_katu=n_katu, n300=n300, n100=n100, n50=n50, n_misses=nmiss, combo=max_combo)

            self.window["-INFO_PP-"].update(f"{str(pp)}pp")

        self.window["-CLI_COMMAND-"].update(self.generate_CLI_command())

        if self.replay is not None and self.values["-ATTR_TIMESTAMP_DATE-"] == "":
            self.values["-ATTR_TIMESTAMP_DATE-"] = self.replay.timestamp.strftime("%d/%m/%Y")
        elif self.values["-ATTR_TIMESTAMP_DATE-"] == "":
            self.values["-ATTR_TIMESTAMP_DATE-"] = datetime.today().strftime("%d/%m/%Y")

        self.window["-ATTR_TIMESTAMP_DATE-"].update(self.values["-ATTR_TIMESTAMP_DATE-"])

        return True

    def switch_layout(self, layout):
        if self.current_layout == layout:
            return
        self.window[self.current_layout].update(visible=False)
        self.window[layout].update(visible=True)

        self.current_layout = layout

    def save_replay(self):
        if not self.attr_check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        os.system(self.generate_CLI_command(self.replay_path))

    def save_as_replay(self):
        if not self.attr_check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        path = psg.popup_get_file("Save as...", save_as=True, no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            os.system(self.generate_CLI_command(path))

    def open_replay(self):
        path = psg.popup_get_file("Open file...", no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            self.replay_path = path
            self.replay = Replay.from_path(path)
            self.load_info(self.replay)

    def load_info(self, replay: Replay):
        self.window["-ATTR_USERNAME-"].update(f"{replay.username}")
        self.window["-ATTR_N300-"].update(f"{replay.count_300}")
        self.window["-ATTR_N100-"].update(f"{replay.count_100}")
        self.window["-ATTR_N50-"].update(f"{replay.count_50}")
        self.window["-ATTR_NGEKIS-"].update(f"{replay.count_geki}")
        self.window["-ATTR_NKATUS-"].update(f"{replay.count_katu}")
        self.window["-ATTR_NMISSES-"].update(f"{replay.count_miss}")
        self.window["-ATTR_TOTAL_SCORE-"].update(f"{replay.score}")
        self.window["-ATTR_MAX_COMBO-"].update(f"{replay.max_combo}")
        self.window["-PFC-"].update(replay.perfect)

        self.values["-ATTR_TIMESTAMP_HOUR-"] = replay.timestamp.strftime("%H")
        self.values["-ATTR_TIMESTAMP_MINUTE-"] = replay.timestamp.strftime("%M")
        self.values["-ATTR_TIMESTAMP_SECOND-"] = replay.timestamp.strftime("%S")

        for mod in utils.mods_list():
            self.window[f"-ATTR_MOD_{mod.upper()}-"].update(True if Mod(utils.mods2code([mod])) in self.replay.mods else False)

        beatmap = self.osu_db.get_beatmap_from_hash(replay.beatmap_hash)

        self.life_graph_data = ([x.time for x in self.replay.life_bar_graph], [x.life * 100 for x in self.replay.life_bar_graph])

        self.life_axes.set_xlim(0, self.life_graph_data[0][-1:][0])
        self.life_update_graph()

        self.window["-INFO_BEATMAP-"].update(f"{beatmap.artist} // {beatmap.mapper} - {beatmap.title}")


if __name__ == "__main__":
    app = MainWindow()

    app._start()
