import argparse
import utils


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
                                prog="Replay Editor",
                                description="This tool let you edit osu! replays\n \
                                            For more detailed help check github page\n \
                                            DON'T USE THIS FOR CHEATING!!!",)
    parser.add_argument("path", type=str, help="Path to replay or folder with replays. If it's only argument provided, show info about replay")

    # parser.add_argument("--GUI", "--gui", action="store_true", required=False, help="Start with GUI. All other arguments will be ignored", )  # TODO uncomment this when ui is done

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
