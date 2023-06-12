from osrparse import Replay
from rosu_pp_py import Beatmap, Calculator
import pyosudb


def calculate_acc(count_300: int = 0, count_100: int = 0, count_50: int = 0, count_miss: int = 0) -> float:
    try:
        return round(((300 * count_300 + 100 * count_100 + 50 * count_50)/(300 * (count_300 + count_100 + count_50 + count_miss))) * 100, 2)
    except ZeroDivisionError:
        return 100.00


def calculate_pp(replay: Replay) -> float:
    pyosudb.parse_osudb("")


if __name__ == "__main__":
    replay = Replay.from_path(r"D:\Games\osu!\Replays\OlegSuperBro - Irodorimidori - Bokura no Freedom DiVE [FOUR DIMENSIONS] (2023-05-28) Osu.osr")
    print(calculate_acc(replay))
