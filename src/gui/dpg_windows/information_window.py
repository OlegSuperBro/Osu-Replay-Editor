import dearpygui.dearpygui as dpg
from pathlib import Path
from osrparse import Replay
from pyosutools.db.osu import Osudb

import calculation
from config import CONFIG


class InformationWindow:
    def __init__(self) -> None:
        self._id = self._build()

    def _build(self) -> int:
        with dpg.tab(label="Replay Information", tag="info_window") as _id:
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Beatmap name")
                    dpg.add_spacer()
                    dpg.add_text("Total accuracy")
                    dpg.add_text("Total pp")
                with dpg.group():
                    dpg.add_text(tag="beatmap_name")
                    dpg.add_text(tag="total_accuracy")
                    dpg.add_text(tag="total_pp")
            return _id

    def update(self, osu_db: Osudb, replay: Replay = None):
        acc = calculation.calculate_acc(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)
        pp = 0

        if replay.game_version != 0:
            beatmap = osu_db.get_beatmap_from_hash(replay.beatmap_hash)
            beatmap_path = str(Path(CONFIG.osu_path) / "songs" / beatmap.folder_name / beatmap.osu_file)
            pp = calculation.calculate_pp(beatmap_path, mode=replay.mode, mods=replay.mods,
                                          n_geki=replay.count_geki, n_katu=replay.count_katu, n300=replay.count_300, n100=replay.count_100, n50=replay.count_50, n_misses=replay.count_miss, combo=replay.max_combo)

        dpg.set_value("total_accuracy", acc)
        dpg.set_value("total_pp", f"{str(pp)}pp")

    def update_on_load(self, osu_db: Osudb, replay: Replay = None):
        beatmap_name = "None"
        if replay.game_version != 0:
            beatmap = osu_db.get_beatmap_from_hash(replay.beatmap_hash)
            beatmap_name = f"{beatmap.artist} / {beatmap.title}"

        dpg.set_value("beatmap_name", beatmap_name)
