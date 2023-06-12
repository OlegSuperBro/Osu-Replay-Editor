from osrparse import Replay
from rosu_pp_py import Beatmap, Calculator
import pyosudb


def calculate_acc(replay: Replay) -> float:
    return round(((300 * replay.count_300 + 100 * replay.count_100 + 50 * replay.count_50)/(300 * (replay.count_300 + replay.count_100 + replay.count_50 + replay.count_miss))) * 100, 2)


def calculate_pp(replay: Replay) -> float:
    pyosudb.parse_osudb("")


if __name__ == "__main__":
    replay = Replay.from_path(r"D:\Games\osu!\Replays\OlegSuperBro - Irodorimidori - Bokura no Freedom DiVE [FOUR DIMENSIONS] (2023-05-28) Osu.osr")
    print(calculate_acc(replay))
