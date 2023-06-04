import PySimpleGUI as psg
from os.path import isfile
from osrparse import Replay, Mod

import utils


def generate_mods_checkboxes(replay, width: int):
    active_mods = utils.code2mods(replay.mods)
    layout = []
    tmp_layout = []
    x = 0
    for mod in list(utils.MODS_2_CODES.keys())[1:]:
        if x > width:
            layout.append(tmp_layout)
            tmp_layout = []
            x = 0

        tmp_layout.append(psg.Text(mod))
        tmp_layout.append(psg.Checkbox("", key=f"-MOD_{mod.upper()}-", default=True if mod in active_mods else False))
        x += 1
    if tmp_layout != []:
        layout.append(tmp_layout)
    return layout


class App:
    def __init__(self, replay: Replay = None, replay_path: str = "") -> None:
        self.current_mode = "simple"
        self.opened_replay = replay
        self.replay_path = replay_path
        self.window = self.create_window()

        self.BUTTON_FUNCS = {
            "-UPDATE-": lambda: self.update_info(),
            "-OPEN_REPLAY-": lambda: self.open_replay(),
            "-SAVE-": lambda: self.save_replay(),
            "-SAVEAS-": lambda: self.save_as_replay(),
            "-CHANGE_LAYOUT-": lambda: self.switch_layout(),
            }

    def main_loop(self) -> None:
        while True:
            self.event, self.values = self.window.read()

            if self.event == psg.WIN_CLOSED or self.event == "-EXIT-":
                break

            self.event = self.event.split("::")[-1:][0]  # bruh

            try:
                self.BUTTON_FUNCS.get(self.event)()
            except TypeError:
                print(f"WARNING: FUNC FOR \"{self.event}\" DON'T EXIST")

    def display_error(self, error_msg):
        psg.popup(error_msg, title="ERROR")

    def check_info(self):
        for value_name, value_of_value in self.values.items():
            value_correct, value_limit = utils.check_limit(value_name, value_of_value)
            if not value_correct:
                self.display_error(f"{value_name} not in {value_limit}")
                return False
        return True

    def update_info(self):
        if not self.check_info():
            return False

        # TODO add things from advanced mode
        self.opened_replay.username = str(self.values["-USERNAME-"])
        self.opened_replay.count_300 = int(self.values["-N300-"])
        self.opened_replay.count_100 = int(self.values["-N100-"])
        self.opened_replay.count_50 = int(self.values["-N50-"])
        self.opened_replay.count_geki = int(self.values["-NGEKIS-"])
        self.opened_replay.count_katu = int(self.values["-NKATUS-"])
        self.opened_replay.count_miss = int(self.values["-NMISSES-"])
        self.opened_replay.score = int(self.values["-TOTAL_SCORE-"])
        self.opened_replay.max_combo = int(self.values["-MAX_COMBO-"])
        self.opened_replay.perfect = bool(self.values["-PFC-"])
        self.opened_replay.mods = self.get_mods()

        return True

    def get_mods(self):
        mods = []
        for mod in list(utils.MODS_2_CODES.keys())[1:]:
            if self.values[f"-MOD_{mod.upper()}-"] is True:
                mods.append(mod)
        return Mod(utils.mods2code(mods))

    def create_window(self):
        if self.opened_replay is None:
            LAYOUT = [[psg.Text("Please, open a file")]]
            return psg.Window("Osu replay editor", LAYOUT)
        MENU_LAYOUT = [['&File', ['&Open::-OPEN_REPLAY-', '&Save::-SAVE-', '&Save As...::-SAVEAS-', '---', 'E&xit::-EXIT-']]]

        SIMPLE_CHANGING_COL = [[psg.Text("Player"), psg.Multiline(self.opened_replay.username, key="-USERNAME-", size=(50, 5))],
                               [psg.Text("300s"), psg.Input(default_text=self.opened_replay.count_300, key="-N300-", size=(6, 1))],
                               [psg.Text("100s"), psg.Input(default_text=self.opened_replay.count_100, key="-N100-", size=(6, 1))],
                               [psg.Text("50s"), psg.Input(default_text=self.opened_replay.count_50, key="-N50-", size=(6, 1))],
                               [psg.Text("Gekis"), psg.Input(default_text=self.opened_replay.count_geki, key="-NGEKIS-", size=(6, 1))],
                               [psg.Text("Katus"), psg.Input(default_text=self.opened_replay.count_katu, key="-NKATUS-", size=(6, 1))],
                               [psg.Text("Misses"), psg.Input(default_text=self.opened_replay.count_miss, key="-NMISSES-", size=(6, 1))],
                               [psg.Text("Total score"), psg.Input(default_text=self.opened_replay.score, key="-TOTAL_SCORE-", size=(11, 1))],
                               [psg.Text("Max combo"), psg.Input(default_text=self.opened_replay.max_combo, key="-MAX_COMBO-", size=(6, 1))],
                               [psg.Text("Perfect combo"), psg.Checkbox("", key="-PFC-")],
                               [psg.Frame("Mods", generate_mods_checkboxes(self.opened_replay, 6))],
                               [psg.Button("Update", key="-UPDATE-")]]

        SIMPLE_INFO_COL = [[psg.Text("Nothing here for now :(")]]

        ADVANCED_CHANGING_COL = [[psg.Text("Game mode"), psg.Combo(values=["osu", "taiko", "catch", "mania"], default_value=utils.code2mode(self.opened_replay.mode.value), key="-GAMEMODE-", readonly=True)],
                                 [psg.Text("test2")]]

        ADVANCED_INFO_COL = [[psg.Text("test3")],
                             [psg.Text("test3")]]

        SIMPLE_MAIN_LAYOUT = [[psg.Menu(MENU_LAYOUT)],
                              [psg.Column(SIMPLE_CHANGING_COL), psg.Column(SIMPLE_INFO_COL)]]

        ADVANCED_MAIN_LAYOUT = [[[psg.Column(ADVANCED_CHANGING_COL), psg.Column(ADVANCED_INFO_COL)]]]

        if self.current_mode == "simple":
            return psg.Window("Osu replay editor", SIMPLE_MAIN_LAYOUT)

        elif self.current_mode == "advanced":
            return psg.Window("Osu replay editor", ADVANCED_MAIN_LAYOUT)

    def switch_layout(self):
        if self.current_mode == "simple":
            self.current_mode = "advanced"

        elif self.current_mode == "advanced":
            self.current_mode = "simple"

        self.window.close()
        self.window = self.create_window()

    def save_replay(self):
        if not self.update_info():
            return

        if isfile(str(self.replay_path)):
            self.opened_replay.write_path(self.replay_path)

    def save_as_replay(self):
        if not self.update_info():
            return

        path = psg.popup_get_file("Save as...", save_as=True, no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            self.opened_replay.write_path(str(path))

    def open_replay(self):
        path = psg.popup_get_file("Save as...", no_window=True, file_types=(("Osr file", "*.osr"), ("All files", "*.*")))
        if path != "":
            self.opened_replay = Replay.from_path(path)
            self.window.close()
            self.window = self.create_window()


if __name__ == "__main__":
    replay = r"D:\Games\osu!\Replays\OlegSuperBro - Irodorimidori - Bokura no Freedom DiVE [FOUR DIMENSIONS] (2023-05-28) Osu.osr"
    app = App(Replay.from_path(replay), replay)

    app.main_loop()
