import argparse
from osrparse import Replay, Mod
from os.path import isdir, join, exists
from os import mkdir
import glob

import utils

# Format of output for --info argument
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
                              mods=", ".join([utils.code2mods(replay.mods)]),
                              date=replay.timestamp,
                              score_id=replay.replay_id))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
                                prog="Replay Editor",
                                description="This tool let you edit osu! replays\n \
                                            For more detailed help check github page\n \
                                            DON'T USE THIS FOR CHEATING!!!",)
    parser.add_argument("path", type=str, help="Path to replay or folder with replays. If it's only argument provided, show info about replay")

    parser.add_argument("--nickname", type=str, help="Set a nickname")

    parser.add_argument("--n300", type=int, metavar="0-65535", help="Set amount of 300s")
    parser.add_argument("--n100", type=int, metavar="0-65535", help="Set amount of 100s")
    parser.add_argument("--n50", type=int, metavar="0-65535", help="Set amount of 50s")
    parser.add_argument("--ngekis", type=int, metavar="0-65535", help="Set amount of gekis (different 300s)")
    parser.add_argument("--nkatus", type=int, metavar="0-65535", help="Set amount of katus (different 100s)")
    parser.add_argument("--nmisses", type=int, metavar="0-65535", help="Set amount of misses")

    parser.add_argument("--score", type=int, metavar="0-2147483647", help="Set replay total score")
    parser.add_argument("--maxcombo", type=int, metavar="0-65535", help="Set maximum combo")
    parser.add_argument("--pfc", type=bool, metavar="True/False", help="Display \"Perfect\" text in life graph")

    parser.add_argument("--mods", type=str, metavar="mod,mod,...", help="Set mods for replay")
    parser.add_argument("--rawmods", type=int, metavar="code", help="Set mods for replay using raw value (check .osr file format wiki)")

    parser.add_argument("--time", type=int, metavar="86400-inf", help="Set replay date using windows ticks")

    parser.add_argument("--info", action="store_true", help="Show info about replay/replays")
    parser.add_argument("-o", "--output", type=str, metavar="path", help="Set output file")

    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()

    replays = []

    if isdir(args.path):
        for file in glob.glob(join(args.path, "*.osr")):
            tmp_replay = Replay.from_path(file)
            tmp_replay.path = file
            replays.append(tmp_replay)

    else:
        tmp_replay = Replay.from_path(args.path)
        tmp_replay.path = args.path
        replays.append(tmp_replay)

    del tmp_replay

    if args.nickname is not None:
        for replay in replays:
            replay.username = args.nickname

    if args.n300 is not None:
        for replay in replays:
            replay.count_300 = args.n300

    if args.n100 is not None:
        for replay in replays:
            replay.count_100 = args.n100

    if args.n50 is not None:
        for replay in replays:
            replay.count_50 = args.n50

    if args.ngekis is not None:
        for replay in replays:
            replay.count_geki = args.ngekis

    if args.nkatus is not None:
        for replay in replays:
            replay.count_katu = args.nkatus

    if args.nmisses is not None:
        for replay in replays:
            replay.count_miss = args.nmisses

    if args.score is not None:
        for replay in replays:
            replay.score = args.score

    if args.maxcombo is not None:
        for replay in replays:
            replay.max_combo = args.maxcombo

    if args.pfc is not None:
        for replay in replays:
            replay.perfect = args.pfc

    if args.mods is not None:
        for replay in replays:
            replay.mods = Mod(utils.mods2code(args.mods))

    if args.rawmods is not None:
        for replay in replays:
            replay.mods = Mod(args.rawmods)

    if args.time is not None:
        for replay in replays:
            replay.timestamp = utils.ticks2date(args.time)

    if args.info:
        for replay in replays:
            print("Replay: " + replay.path)
            show_replay_info(replay)

    if args.output is not None:
        # if only 1 replay given
        if len(replays) == 1:
            replays[0].write_path(args.output)
            exit()

        # if more than 1 replay given, create directory
        else:
            if not exists(args.output):
                mkdir(args.output)

            for index, replay in enumerate(replays):
                replay.write_path(join(args.output, f"{index}.osr"))
