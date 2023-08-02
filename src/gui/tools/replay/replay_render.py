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
        closest_event_index = self.get_closest_event_index(replay_data, timestamp)

        prev_event: ReplayEventOsu = replay_data[closest_event_index - 1]
        event: ReplayEventOsu = replay_data[closest_event_index]

        time_delta = event.time_delta - prev_event.time_delta
        timestamp_delta = timestamp - prev_event.time_delta
        time_passed_percent = timestamp_delta / time_delta if timestamp_delta != 0 else 1

        x_delta = event.x - prev_event.x
        y_delta = event.y - prev_event.y

        x = prev_event.x + x_delta * time_passed_percent
        y = prev_event.y + y_delta * time_passed_percent
        self.drawer.draw_cursor(x, y, self.DEFAULT_OFFSET)

    def get_closest_event_index(self, replay_data: List[ReplayEventOsu], timestamp: int):
        for index, event in enumerate(replay_data):
            if timestamp <= event.time_delta:
                return index
