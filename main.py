from osrparse import Replay
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
                              mods=replay.mods,
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

    if args.gekis is not None:
        show_info = False

        for replay in replays:
            replay.count_geki = args.gekis

    if args.katus is not None:
        show_info = False

        for replay in replays:
            replay.count_katu = args.katus

    if args.misses is not None:
        show_info = False

        for replay in replays:
            replay.count_miss = args.misses

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
            replay.mods = args.mods  # TODO change to parser for code2mods and mods2code

    if args.rawmods is not None:
        show_info = False

        for replay in replays:
            replay.mods = args.rawmods

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