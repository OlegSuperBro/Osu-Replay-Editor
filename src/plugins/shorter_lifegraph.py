from lib.plugin.utils import on_replay_load
from lib.plugin import var_types

from typing import List
from osrparse.utils import LifeBarState


def decrease_lifebar_length(lifebar: List[LifeBarState]) -> List[LifeBarState]:
    new_lifebar = []
    for index in range(len(lifebar)):
        if index == 0 or index >= len(lifebar) - 1:
            new_lifebar.append(lifebar[index])
            continue

        if lifebar[index].life != lifebar[index + 1].life or lifebar[index].life != lifebar[index - 1].life:
            new_lifebar.append(lifebar[index])

    return new_lifebar


@on_replay_load()
def on_load(replay: var_types.Replay):
    replay.life_bar_graph = decrease_lifebar_length(replay.life_bar_graph)
