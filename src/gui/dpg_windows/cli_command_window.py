import dearpygui.dearpygui as dpg
import pyperclip
from osrparse import Replay

import utils


class CliCommandWindow:
    def __init__(self) -> None:
        self._id = self._build()

    def _build(self) -> None:
        with dpg.window(label="CLI command", pos=(0, 807), width=650, min_size=(400, 50), no_scrollbar=True, max_size=(30000, 50), tag="CLI_window", on_close=lambda: dpg.hide_item("CLI_window")) as _id:
            with dpg.group(horizontal=True):
                dpg.add_input_text(width=-135, readonly=True, tag="cli_command")
                dpg.add_button(label="Copy to clipboard", callback=self.clipboard_copy_CLI_command)
            return _id

    def update(self, replay: Replay) -> None:
        dpg.set_value("cli_command", self.generate_CLI_command(replay))

    def update_on_load(self, replay: Replay) -> None:
        self.update(replay)

    def generate_CLI_command(self, replay: Replay, input_path: str = "[input]", output_path: str = "[output]"):
        lifebar = utils.lifebar2str(replay.life_bar_graph) if replay.replay_data is not None else None
        return utils.generate_command(input_path,
                                      replay.username, replay.count_300, replay.count_100, replay.count_50, replay.count_geki, replay.count_katu, replay.count_miss,
                                      replay.score, replay.max_combo, replay.perfect, None, replay.mods, utils.date2windows_ticks(replay.timestamp), lifebar, output_path)

    def clipboard_copy_CLI_command(self):
        pyperclip.copy(self.generate_CLI_command())
