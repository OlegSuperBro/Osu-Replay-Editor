from osrparse import Replay, GameMode, Mod
from rosu_pp_py import Beatmap, Calculator
from pathlib import Path
import pyosudb

from config import CONFIG


def calculate_acc(count_300: int = 0, count_100: int = 0, count_50: int = 0, count_miss: int = 0) -> float:
    try:
        return round(((300 * count_300 + 100 * count_100 + 50 * count_50)/(300 * (count_300 + count_100 + count_50 + count_miss))) * 100, 2)
    except ZeroDivisionError:
        return 100.00


def replay_calculate_acc(replay: Replay):
    return calculate_acc(replay.count_300, replay.count_100, replay.count_50,  replay.count_miss)


def calculate_pp(beatmap_path: str, mode: GameMode = 0, mods: Mod = Mod(0),
                 n_geki: int = 0, n_katu: int = 0, n300: int = 0, n100: int = 0, n50: int = 0, n_misses: int = 0, combo: int = 0) -> float:
    beatmap = Beatmap(path=beatmap_path)
    calc = Calculator(mode=mode.value, mods=mods.value, acc=calculate_acc(),
                      n_geki=n_geki, n_katu=n_katu, n300=n300, n100=n100, n50=n50, n_misses=n_misses,
                      combo=combo)
    return round(calc.performance(beatmap).pp, 2)


def replay_calculate_pp(replay: Replay):
    db = pyosudb.parse_osudb(Path(CONFIG.get("osu_path")) / "osu!.db")
    beatmap = db.get_beatmap_from_hash(replay.beatmap_hash)
    beatmap_path = str(Path(CONFIG.get("osu_path")) / "songs" / beatmap.folder_name / beatmap.osu_file)
    return calculate_pp(beatmap_path, mode=replay.mode, mods=replay.mods,
                        n_geki=replay.count_geki, n_katu=replay.count_katu, n300=replay.count_300, n100=replay.count_100, n50=replay.count_50, n_misses=replay.count_miss,
                        combo=replay.max_combo)


if __name__ == "__main__":
    replay = Replay.from_path(r"D:\Games\osu!\Replays\OlegSuperBro - BAND-MAID - CROSS [DECA'S EXTRA] (2023-06-19) Osu.osr")
    print(replay_calculate_acc(replay))
    print(replay_calculate_pp(replay))
