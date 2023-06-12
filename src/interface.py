import PySimpleGUI as psg
import os
from osrparse import Replay, Mod
from pyosudb import parse_osudb
from pathlib import Path

import utils
import calculation
from config import CONFIG


def generate_mods_checkboxes(width: int):
    layout = []
    tmp_layout = []
    x = 0
    for mod in list(utils.MODS_2_CODES.keys())[1:]:
        if x > width:
            layout.append(tmp_layout)
            tmp_layout = []
            x = 0

        tmp_layout.append(psg.Text(mod))
        tmp_layout.append(psg.Checkbox("", key=f"-MOD_{mod.upper()}-", default=False))
        x += 1
    if tmp_layout != []:
        layout.append(tmp_layout)
    return layout


class App:
    def __init__(self) -> None:
        self.window = self.create_window()
        self.osu_db = parse_osudb(Path(CONFIG.get("osu_path")) / "osu!.db")
        self.replay_path = None

        self.BUTTON_FUNCS = {
            "-OPEN_REPLAY-": lambda: self.open_replay(),
            "-SAVE-": lambda: self.save_replay(),
            "-SAVEAS-": lambda: self.save_as_replay(),
            }

    def main_loop(self) -> None:
        while True:
            self.event, self.values = self.window.read(timeout=10)

            if self.event == psg.WIN_CLOSED or self.event == "-EXIT-":
                break

            self.event = self.event.split("::")[-1:][0]  # bruh

            try:
                self.BUTTON_FUNCS.get(self.event)()
            except TypeError:
                pass

            self.update_info()

    def create_window(self):
        MENU_LAYOUT = [['&File', ['&Open::-OPEN_REPLAY-', '&Save::-SAVE-', '&Save As...::-SAVEAS-', '---', 'E&xit::-EXIT-']]]

        CHANGING_COL = [[psg.Text("Player"), psg.Multiline(default_text="", key="-USERNAME-", size=(50, 5)), psg.Text("", key="-USERNAME_ERROR-")],
                        [psg.Text("300s"), psg.Input(default_text="0", key="-N300-", size=(6, 1)), psg.Text("", key="-N300_ERROR-")],
                        [psg.Text("100s"), psg.Input(default_text="0", key="-N100-", size=(6, 1)), psg.Text("", key="-N100_ERROR-")],
                        [psg.Text("50s"), psg.Input(default_text="0", key="-N50-", size=(6, 1)), psg.Text("", key="-N50_ERROR-")],
                        [psg.Text("Gekis"), psg.Input(default_text="0", key="-NGEKIS-", size=(6, 1)), psg.Text("", key="-NGEKIS_ERROR-")],
                        [psg.Text("Katus"), psg.Input(default_text="0", key="-NKATUS-", size=(6, 1)), psg.Text("", key="-NKATUS_ERROR-")],
                        [psg.Text("Misses"), psg.Input(default_text="0", key="-NMISSES-", size=(6, 1)), psg.Text("", key="-NMISSES_ERROR-")],
                        [psg.Text("Total score"), psg.Input(default_text="0", key="-TOTAL_SCORE-", size=(11, 1)), psg.Text("", key="-TOTAL_SCORE_ERROR-")],
                        [psg.Text("Max combo"), psg.Input(default_text="0", key="-MAX_COMBO-", size=(6, 1)), psg.Text("", key="-MAX_COMBO_ERROR-")],
                        [psg.Text("Perfect combo"), psg.Checkbox("", key="-PFC-",)],
                        [psg.Frame("Mods", generate_mods_checkboxes(6))]]

        INFO_COL = [[psg.Text("Beatmap: "), psg.Text("None", key="-INFO_BEATMAP-")],
                    [psg.Text("Total accuracy: "), psg.Text("None", key="-INFO_ACCURACY-")]]

        MAIN_LAYOUT = [[psg.Menu(MENU_LAYOUT)],
                       [psg.Column(CHANGING_COL), psg.Column(INFO_COL)],
                       [psg.Text("CLI command")],
                       [psg.InputText(key="-CLI_COMMAND-", readonly=True, expand_x=True)]]

        return psg.Window("Osu replay editor", MAIN_LAYOUT, finalize=True, resizable=True)

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

        n300, n100, n50, nmiss = int(self.values["-N300-"]), int(self.values["-N100-"]), int(self.values["-N50-"]), int(self.values["-NMISSES-"])

        self.window["-INFO_ACCURACY-"].update(f"{str(calculation.calculate_acc(n300, n100, n50, nmiss))}%")
        self.window["-CLI_COMMAND-"].update(self.generate_CLI_command())

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

    def generate_CLI_command(self, input_path: str = "[path]", output_path: str = "[output]"):
        return utils.generate_command(input_path,
                                      self.values["-USERNAME-"], self.values["-N300-"], self.values["-N100-"], self.values["-N50-"],
                                      self.values["-NGEKIS-"], self.values["-NKATUS-"], self.values["-NMISSES-"], self.values["-TOTAL_SCORE-"],
                                      self.values["-MAX_COMBO-"], self.values["-PFC-"], None, self.get_mods(), None, output_path)
                                                                                                       #TODO change to time

    def get_mods(self):
        mods = []
        for mod in list(utils.MODS_2_CODES.keys())[1:]:
            if self.values[f"-MOD_{mod.upper()}-"] is True:
                mods.append(mod)
        return Mod(utils.mods2code(mods))

    def save_replay(self):
        if not self.check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        print(self.generate_CLI_command(self.replay_path, self.replay_path))
        os.system(self.generate_CLI_command(self.replay_path, self.replay_path))

    def save_as_replay(self):
        if not self.check_info():
            return

        if self.replay_path is None:
            self.show_error("Please, open replay first")
            return

        path = psg.popup_get_file("Save as...", save_as=True, no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            print(self.generate_CLI_command(self.replay_path, path))
            os.system(self.generate_CLI_command(self.replay_path, path))

    def open_replay(self):
        path = psg.popup_get_file("Open file...", no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            self.replay_path = path
            replay = Replay.from_path(path)

            self.window["-USERNAME-"].update(f"{replay.username}")
            self.window["-N300-"].update(f"{replay.count_300}")
            self.window["-N100-"].update(f"{replay.count_100}")
            self.window["-N50-"].update(f"{replay.count_50}")
            self.window["-NGEKIS-"].update(f"{replay.count_geki}")
            self.window["-NKATUS-"].update(f"{replay.count_katu}")
            self.window["-NMISSES-"].update(f"{replay.count_miss}")
            self.window["-TOTAL_SCORE-"].update(f"{replay.score}")
            self.window["-MAX_COMBO-"].update(f"{replay.max_combo}")
            self.window["-PFC-"].update(replay.perfect)

            beatmap = self.osu_db.get_beatmap_from_hash(replay.beatmap_hash)
            self.window["-INFO_BEATMAP-"].update(f"{beatmap.artist} // {beatmap.mapper} - {beatmap.title}")

            for mod in list(utils.MODS_2_CODES.keys())[1:]:
                self.window[f"-MOD_{mod.upper()}-"].update(True if Mod(utils.mods2code([mod])) in replay.mods else False)


if __name__ == "__main__":
    app = App()

    app.main_loop()
