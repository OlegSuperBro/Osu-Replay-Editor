from typing import List
from osrparse import ReplayEventOsu

from utils import Mod


def cs2pixels(cs):
    """
    size in osu!pixels (same size as pixel size with 640x480 resolution)
    """
    return int((54.4 - 4.48 * cs))


def ar2full_time(ar):
    """
    ar in ms
    """
    if ar < 5:
        return 1200 + 600 * (5 - ar) / 5
    if ar == 5:
        return 1200
    if ar > 5:
        return 1200 - 750 * (ar - 5) / 5


def full_time2ar(ms):
    if ms > 1200:
        return 5 - (ms - 1200) / (600 / 5)
    if ms == 1200:
        return 5
    if ms < 1200:
        return 5 + (1200 - ms) / (750 / 5)


def ar2fadein_time(ar):
    """
    fade in for ar in ms
    """
    if ar < 5:
        return 800 + 400 * (5 - ar) / 5
    if ar == 5:
        return 800
    if ar > 5:
        return 800 - 500 * (ar - 5) / 5


def apply_mods2cs(cs: int, mod: Mod):
    pass


def apply_mods2ar(ar: int, mods: Mod):
    if Mod["Easy"] in mods:
        ar /= 2
    if Mod["HardRock"] in mods:
        ar *= 1.4
        ar = min(ar, 10)
    if Mod["DoubleTime"] in mods or Mod["Nightcore"] in mods:
        ar = round(full_time2ar(ar2full_time(ar) - ar2full_time(ar) * 0.33), 2)
    elif Mod["HalfTime"] in mods:
        ar = round(full_time2ar(ar2full_time(ar) + ar2full_time(ar) * 0.33), 2)

    return ar


def apply_mods2od(od: int, mod: Mod):
    pass


def update_replay_data(events: List[ReplayEventOsu]) -> List[ReplayEventOsu]:
    total_ticks = 0
    tmp_events = []

    for event in events:
        total_ticks += event.time_delta
        tmp_events.append(ReplayEventOsu(total_ticks, event.x, event.y, event.keys))
    return tmp_events
