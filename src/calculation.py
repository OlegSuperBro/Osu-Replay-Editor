from osrparse import Replay, GameMode, Mod
from rosu_pp_py import Beatmap, Calculator


def calculate_acc(count_300: int = 0, count_100: int = 0, count_50: int = 0, count_miss: int = 0) -> float:
    try:
        return round(((300 * count_300 + 100 * count_100 + 50 * count_50)/(300 * (count_300 + count_100 + count_50 + count_miss))) * 100, 2)
    except ZeroDivisionError:
        return 100.00


def replay_calculate_acc(replay: Replay):
    return calculate_acc(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)


def calculate_pp(beatmap_path: str, mode: GameMode = 0, mods: Mod = Mod(0),
                 n_geki: int = 0, n_katu: int = 0, n300: int = 0, n100: int = 0, n50: int = 0, n_misses: int = 0, combo: int = 0) -> float:
    beatmap = Beatmap(path=beatmap_path)
    calc = Calculator(mode=mode.value, mods=mods.value, acc=calculate_acc(),
                      n_geki=n_geki, n_katu=n_katu, n300=n300, n100=n100, n50=n50, n_misses=n_misses,
                      combo=combo)
    return round(calc.performance(beatmap).pp, 2)
