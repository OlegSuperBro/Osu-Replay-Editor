from dearpygui import dearpygui as dpg
from osrparse import Replay, ReplayEventOsu
from typing import List, Tuple, Union

from .skin import Skin


class _Drawer:
    CURSOR_SIZE = 50

    def __init__(self, skin: Skin, drawlist_tag: Union[int, str]) -> None:
        self.skin = skin
        self.drawlist_tag = drawlist_tag

    def draw_cursor(self, x: int, y: int, offset: Tuple[int, int] = (0, 0)):
        dpg.draw_image(self.skin.cursor_middle,
                       (x - self.CURSOR_SIZE / 2 + offset[0], y - self.CURSOR_SIZE / 2 + offset[1]),
                       (x + self.CURSOR_SIZE / 2 + offset[0], y + self.CURSOR_SIZE / 2 + offset[1]),
                       parent=self.drawlist_tag)

        dpg.draw_image(self.skin.cursor,
                       (x - self.CURSOR_SIZE / 2 + offset[0], y - self.CURSOR_SIZE / 2 + offset[1]),
                       (x + self.CURSOR_SIZE / 2 + offset[0], y + self.CURSOR_SIZE / 2 + offset[1]),
                       parent=self.drawlist_tag)


class ReplayRender:
    DEFAULT_OFFSET = (64, 48)

    def __init__(self, skin: Skin, parent: Union[int, str]) -> None:
        self.drawer = _Drawer(skin, parent)

    def render_frame(self, replay_data: List[ReplayEventOsu], timestamp: int):
        closest_event_timestamp = -1
        closest_event_index = None
        for index in range(len(replay_data)):
            event = replay_data[index]
            to_timestamp = abs(timestamp - event.time_delta)
            if to_timestamp < closest_event_timestamp or closest_event_timestamp == -1:
                closest_event_index = index
                closest_event_timestamp = to_timestamp

        prev_event = replay_data[closest_event_index - 1]
        event = replay_data[closest_event_index]
        x, y = event.x, event.y
        self.drawer.draw_cursor(x, y, self.DEFAULT_OFFSET)
