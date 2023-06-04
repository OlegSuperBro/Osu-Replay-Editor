import datetime

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

CODE_2_MODE = {
    0: "osu",
    1: "taiko",
    2: "catch",
    3: "mania"
}

MODE_2_CODE = {
    "osu": 0,
    "taiko": 1,
    "catch": 2,
    "mania": 3,
}

VALUES_LIMITS = {
    "-GAME_VER-": range(0, 2147483647),
    "-N300-": range(0, 65535),
    "-N100-": range(0, 65535),
    "-N50-": range(0, 65535),
    "-NGEKIS-": range(0, 65535),
    "-NKATUS-": range(0, 65535),
    "-NMISSES-": range(0, 65535),
    "-TOTAL_SCORE-": range(0, 2147483647),
    "-MAX_COMBO-": range(0, 65535),
}


def check_limit(name: str, value: any) -> tuple[bool, int]:
    limit = VALUES_LIMITS.get(name)
    if limit is None:
        return (True, VALUES_LIMITS.get(name))

    if not (is_int(value)):
        return (False, VALUES_LIMITS.get(name))
    if not (VALUES_LIMITS.get(name).start <= int(value) <= VALUES_LIMITS.get(name).stop):
        return (False, VALUES_LIMITS.get(name))

    return (True, VALUES_LIMITS.get(name))


def code2mode(code: int) -> str:
    return CODE_2_MODE.get(code)


def mode2code(mode: str) -> int:
    return MODE_2_CODE.get(mode)


def mods2code(mods: list[str]) -> int:
    return sum([MODS_2_CODES.get(mod) for mod in mods])


def code2mods(code: int) -> str:
    mod_list = []
    code = bin(code)[:1:-1]
    for i in range(len(CODES_2_MODS.keys())):
        try:
            if code[i] == "1":
                mod_list.append(CODES_2_MODS.get(1 << i))
        except IndexError:
            break
    return mod_list


def ticks2date(ticks) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ticks, tz=datetime.timezone.utc)


def get_from_tree(dictionary: dict, *path: any) -> any:
    value = dictionary
    for key in path:
        try:
            value = value.get(key)
        except KeyError:
            return None
    return value


def is_int(value: any):
    try:
        assert int(value) == float(value)
    except (AssertionError, ValueError):
        return False
    else:
        return True
