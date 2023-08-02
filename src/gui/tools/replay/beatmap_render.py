from dearpygui import dearpygui as dpg
from pyosutools.beatmaps.beatmap import Beatmap
from pyosutools.beatmaps.datatypes import CircleObject, SliderObject, SpinnerObject, SliderType, CurvePoint
from typing import List, Tuple, Union

from .skin import Skin
from .utils import cs2pixels, ar2fadein_time, ar2full_time


class _Drawer:
    NUMBER_OFFSET = (50, 50)

    def __init__(self, skin: Skin, drawlist_tag: Union[int, str]) -> None:
        self.skin = skin
        self.drawlist_tag = drawlist_tag

    def draw_hit_circle(self, x: int, y: int, cs: int, index: Union[int, None] = None, combo_colour: Tuple[int, int, int] = (255, 255, 255), offset: Tuple[int, int] = (0, 0), alpha: int = 255):
        dpg.draw_image(self.skin.hitcircle,
                       (x - cs2pixels(cs) + offset[0], y - cs2pixels(cs) + offset[1]),
                       (x + cs2pixels(cs) + offset[0], y + cs2pixels(cs) + offset[1]),
                       color=list(combo_colour) + [alpha],
                       parent=self.drawlist_tag)

        dpg.draw_image(self.skin.hitcircle_overlay,
                       (x - cs2pixels(cs) + offset[0], y - cs2pixels(cs) + offset[1]),
                       (x + cs2pixels(cs) + offset[0], y + cs2pixels(cs) + offset[1]),
                       color=[255, 255, 255] + [alpha],
                       parent=self.drawlist_tag)

        if index is not None:
            dpg.draw_image(self.skin.default_numbers[index],
                           (x - cs2pixels(cs) + offset[0] + self.NUMBER_OFFSET[0] / 2, y - cs2pixels(cs) + offset[1] + self.NUMBER_OFFSET[1] / 2),
                           (x + cs2pixels(cs) + offset[0] - self.NUMBER_OFFSET[0] / 2, y + cs2pixels(cs) + offset[1] - self.NUMBER_OFFSET[1] / 2),
                           color=[255, 255, 255] + [alpha],
                           parent=self.drawlist_tag)

    def draw_slider(self, x: int, y: int, cs: int, _type: SliderType, points: List[CurvePoint], index: int = 0, offset: Tuple[int, int] = (0, 0), alpha: int = 255):
        pass


class BeatmapRender:
    DEFAULT_OFFSET = (64, 48)
    PERCENT = 25

    def __init__(self, skin: Skin, parent: Union[int, str]) -> None:
        self.drawer = _Drawer(skin, parent)

    def render_frame(self, beatmap: Beatmap, timestamp: int):
        min_timestamp = beatmap.hit_objects[0].time
        max_timestamp = beatmap.hit_objects[-1:][0].time
        delta_timestamp = max_timestamp - min_timestamp
        count_objects = len(beatmap.hit_objects)

        timestamp_in_percents = ((timestamp - min_timestamp) / (delta_timestamp / 100))

        tmp_objects = beatmap.hit_objects[int(count_objects / 100 * (timestamp_in_percents - self.PERCENT / 2)):int(count_objects / 100 * (timestamp_in_percents + self.PERCENT / 2))]

        full_time = ar2full_time(beatmap.difficulty.approach_rate)
        fade_in_time = ar2fadein_time(beatmap.difficulty.approach_rate)

        for hit_object in tmp_objects[::-1]:
            if type(hit_object) == SliderObject:
                if hit_object.time + hit_object.length < timestamp or hit_object.time + hit_object.length > timestamp + full_time:
                    continue

            elif (hit_object.time < timestamp or hit_object.time > timestamp + full_time):
                continue
            alpha = 255 - int((255 / 100) * abs(timestamp - hit_object.time) / (fade_in_time / 100))
            alpha = max(alpha, 0)

            if type(hit_object) == CircleObject:
                self.drawer.draw_hit_circle(hit_object.x, hit_object.y, beatmap.difficulty.circle_size, 0, beatmap.colours.combo[0], self.DEFAULT_OFFSET, alpha=alpha)
            elif type(hit_object) == SliderObject:
                self.drawer.draw_slider(hit_object.x, hit_object.y, beatmap.difficulty.circle_size, hit_object.curve_type, hit_object.curve_points, 0, self.DEFAULT_OFFSET, alpha=alpha)
            elif type(hit_object) == SpinnerObject:
                pass
