from osrparse import Replay, Mod
from os.path import isdir, join, isfile
from os import mkdir
import glob
import datetime

import CLI

DEFAULT_INFO = \
"""
Gamemode: {gamemode}
Game version: {game_version}
Beatmap hash: {map_hash}
Player: {player}
Replay hash: {replay_hash}
300s: {n300}
100s: {n100}
50s: {n50}
Gekis: {gekis}
Katus: {katus}
Misses: {misses}
Total score: {score}
Max combo: {combo}
Perfect full combo: {pfc}
Mods: {mods}
Date: {date}
Score id: {score_id}
"""

MODS_2_CODES = {
    "nm": 0,
    "nf": 1 << 0,
    "ez": 1 << 1,
    "td": 1 << 2,
    "hd": 1 << 3,
    "hr": 1 << 4,
    "sd": 1 << 5,
    "dt": 1 << 6,
    "rx": 1 << 7,
    "ht": 1 << 8,
    "nc": 1 << 9,
    "fl": 1 << 10,
    "at": 1 << 11,
    "so": 1 << 12,
    "ap": 1 << 13,
    "pf": 1 << 14,
    "4k": 1 << 15,
    "5k": 1 << 16,
    "6k": 1 << 17,
    "7k": 1 << 18,
    "8k": 1 << 19,
    "fd": 1 << 20,
    "rd": 1 << 21,
    "cn": 1 << 22,
    "tp": 1 << 23,
    "9k": 1 << 24,
    "co": 1 << 25,
    "1k": 1 << 26,
    "3k": 1 << 27,
    "2k": 1 << 28,
    "v2": 1 << 29,
    "mr": 1 << 30,
}

CODES_2_MODS = {
    1 << 0: "nm",
    1 << 1: "nf",
    1 << 2: "ez",
    1 << 3: "td",
    1 << 4: "hd",
    1 << 5: "hr",
    1 << 6: "sd",
    1 << 7: "rx",
    1 << 8: "ht",
    1 << 9: "nc",
    1 << 10: "fl",
    1 << 11: "at",
    1 << 12: "so",
    1 << 13: "ap",
    1 << 14: "pf",
    1 << 15: "4k",
    1 << 16: "5k",
    1 << 17: "6k",
    1 << 18: "7k",
    1 << 19: "8k",
    1 << 20: "fd",
    1 << 21: "rd",
    1 << 22: "cn",
    1 << 23: "tp",
    1 << 24: "9k",
    1 << 25: "co",
    1 << 26: "1k",
    1 << 27: "3k",
    1 << 28: "2k",
    1 << 29: "v2",
    1 << 30: "mr",
}


def ticks2date(ticks) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ticks, tz=datetime.timezone.utc)


def show_replay_info(replay: Replay):
    print(DEFAULT_INFO.format(gamemode=replay.mode,
                              game_version=replay.game_version,
                              map_hash=replay.beatmap_hash,
                              player=replay.username,
                              replay_hash=replay.replay_hash,
                              n300=replay.count_300,
                              n100=replay.count_100,
                              n50=replay.count_50,
                              gekis=replay.count_geki,
                              katus=replay.count_katu,
                              misses=replay.count_miss,
                              score=replay.score,
                              combo=replay.max_combo,
                              pfc=replay.perfect,
                              mods=", ".join([CODES_2_MODS.get(mod) for mod in replay.mods]),
                              date=replay.timestamp,
                              score_id=replay.replay_id))


if __name__ == "__main__":
    args = CLI.get_parser().parse_args()

    replays = []
    show_info = True

    if isdir(args.path):
        for file in glob.glob(join(args.path, "*.osr")):
            replays.append(Replay.from_path(file))

    else:
        replays.append(Replay.from_path(args.path))

    # TODO uncomment this when GUI is done
    # if args.GUI:
    #     CUI_loop(replays)

    if args.nickname is not None:
        show_info = False

        for replay in replays:
            replay.username = args.nickname

    if args.n300 is not None:
        show_info = False

        for replay in replays:
            replay.count_300 = args.n300

    if args.n100 is not None:
        show_info = False

        for replay in replays:
            replay.count_100 = args.n100

    if args.n50 is not None:
        show_info = False

        for replay in replays:
            replay.count_50 = args.n50

    if args.ngekis is not None:
        show_info = False

        for replay in replays:
            replay.count_geki = args.ngekis

    if args.nkatus is not None:
        show_info = False

        for replay in replays:
            replay.count_katu = args.nkatus

    if args.nmisses is not None:
        show_info = False

        for replay in replays:
            replay.count_miss = args.nmisses

    if args.score is not None:
        show_info = False

        for replay in replays:
            replay.score = args.score

    if args.maxcombo is not None:
        show_info = False

        for replay in replays:
            replay.max_combo = args.maxcombo

    if args.pfc is not None:
        show_info = False

        for replay in replays:
            replay.perfect = args.pfc

    if args.mods is not None:
        show_info = False

        for replay in replays:
            mods = 0
            for mod in args.mods.split(","):
                mod_code = MODS_2_CODES.get(mod)
                if mod_code is None:
                    raise Exception(f"Mod {mod} don't exist")
                mods += mod_code
            replay.mods = Mod(mods)

    if args.rawmods is not None:
        show_info = False

        for replay in replays:
            replay.mods = Mod(args.rawmods)

    if args.time is not None:
        show_info = False

        for replay in replays:
            replay.timestamp = ticks2date(args.time)

    if show_info and len(replays) == 1:
        show_replay_info(replays[0])

    if args.output:
        if not isfile(args.output):
            try:
                mkdir(args.output)
            except Exception:
                pass

            for index, replay in enumerate(replays):
                replay.write_path(args.output + f"{index}.osr")
        elif len(replays) != 1:
            raise Exception("You can't provide file as output if you provided directory as input")

        else:
            for replay in replays:
                replay.write_path(args.output)
    elif not show_info:
        raise Exception("Please, provide output file/directory")