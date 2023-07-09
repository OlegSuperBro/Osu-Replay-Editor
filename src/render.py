import dearpygui as dpg
from PIL import Image, ImageDraw, ImageShow, ImageFont
from osrparse import Replay, ReplayEventOsu
from pyosutools.beatmaps.beatmap import Beatmap
from pyosutools.beatmaps.datatypes import CircleObject, SliderObject, SpinnerObject, SliderType, CurvePoint
from typing import List, Tuple, Union

from utils import Mod


class Colors:
    HIT_CIRCLE = [255, 0, 0]
    HIT_CIRCLE_OUTLINE = [255, 255, 255]
    HIT_OBJECT_NUMBER = [255, 255, 255]
    SLIDER_BODY = [255, 255, 255]
    SLIDER_BODY_OUTLINE = [255, 0, 0]


class Drawer:
    @staticmethod
    def draw_hit_circle(img: Image, x: int, y: int, cs: int, index: Union[int, None] = 0, offset: Tuple[int, int] = (0, 0), alpha: int = 255):
        draw = ImageDraw.Draw(img)
        draw.ellipse((x - cs2pixels(cs) + offset[0], y - cs2pixels(cs) + offset[1], x + cs2pixels(cs) + offset[0], y + cs2pixels(cs) + offset[1]), fill=tuple(Colors.HIT_CIRCLE + [alpha]), outline=tuple(Colors.HIT_CIRCLE_OUTLINE + [alpha]), width=int((12 / 100 * 9 * (11 - cs))))
        if index is None:
            return

        if cs == 0:
            font = ImageFont.truetype("arial", 60)
        if cs > 0:
            font = ImageFont.truetype("arial", int((60 / 100 * 9 * (11 - cs))))

        text_box = font.getbbox(str(index))
        x_offset = (text_box[0] + text_box[2]) / 2
        y_offset = (text_box[1] + text_box[3]) / 2
        draw.text((x - x_offset + offset[0], y - y_offset + offset[1], x + x_offset + offset[0], y + y_offset + offset[1]), str(index), fill=tuple(Colors.HIT_OBJECT_NUMBER + [alpha]), font=font)

    @staticmethod
    def draw_slider(img: Image, x: int, y: int, cs: int, _type: SliderType, points: List[CurvePoint], index: int = 0, offset: Tuple[int, int] = (0, 0), alpha: int = 255):
        draw = ImageDraw.Draw(img)
        draw.line([(x + offset[0], y + offset[1])] + [(point.x + offset[0], point.y + offset[1]) for point in points], fill=tuple(Colors.SLIDER_BODY + [alpha]), width=10)
        last_point = points[-1:][0]
        Drawer.draw_hit_circle(img, x, y, cs, index, offset=offset, alpha=alpha)
        # print(last_point)
        Drawer.draw_hit_circle(img, last_point.x, last_point.y, cs, None, offset=offset, alpha=alpha)


class ReplayPlayer:
    PERCENT = 25

    def __init__(self, beatmap: Beatmap) -> None:
        self.beatmap = beatmap
        self.frame = None
        self.current_tick = None
        self.note_offset = (cs2pixels(self.beatmap.difficulty.circle_size), cs2pixels(self.beatmap.difficulty.circle_size))

    def loop(self):
        self.render_frame(self.current_tick)

    def render_frame(self, timestamp: int) -> Image:
        img = Image.new("RGBA", (640, 480), (0, 0, 0, 255))
        min_timestamp = self.beatmap.hit_objects[0].time
        max_timestamp = self.beatmap.hit_objects[-1:][0].time
        delta_timestamp = max_timestamp - min_timestamp
        count_objects = len(self.beatmap.hit_objects)

        timestamp_in_percents = ((timestamp - min_timestamp) / (delta_timestamp / 100))

        tmp_objects = self.beatmap.hit_objects[int(count_objects / 100 * (timestamp_in_percents - self.PERCENT / 2)):int(count_objects / 100 * (timestamp_in_percents + self.PERCENT / 2))]

        full_time = ar2full_time(beatmap.difficulty.approach_rate)
        fade_in_time = ar2fadein_time(beatmap.difficulty.approach_rate)
        delta_time = full_time - fade_in_time

        for hit_object in tmp_objects[::-1]:
            if type(hit_object) == SliderObject:
                if hit_object.time + hit_object.length < timestamp or hit_object.time + hit_object.length > timestamp + full_time:
                    continue

            elif (hit_object.time < timestamp or hit_object.time > timestamp + full_time):
                continue
            alpha = 255 - int((255 / 100) * abs(timestamp - hit_object.time) / (fade_in_time / 100))
            if alpha < 0:
                alpha = 0
            # print(timestamp, hit_object.time, full_time, fade_in_time, delta_time, alpha)
            if type(hit_object) == CircleObject:
                Drawer.draw_hit_circle(img, hit_object.x, hit_object.y, self.beatmap.difficulty.circle_size, 0, self.note_offset, alpha=alpha)
                # pass
            elif type(hit_object) == SliderObject:
                Drawer.draw_slider(img, hit_object.x, hit_object.y, self.beatmap.difficulty.circle_size, hit_object.curve_type, hit_object.curve_points, 0, self.note_offset, alpha=alpha)
            elif type(hit_object) == SpinnerObject:
                pass
        return img


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
        if ar > 10:
            ar = 10
    if Mod["DoubleTime"] in mods or Mod["Nightcore"] in mods:
        ar = round(full_time2ar(ar2full_time(ar) - ar2full_time(ar) * 0.33), 2)
    elif Mod["HalfTime"] in mods:
        ar = round(full_time2ar(ar2full_time(ar) + ar2full_time(ar) * 0.33), 2)

    return ar


def apply_mods2od(od: int, mod: Mod):
    pass


if __name__ == "__main__":
    # those things is used only for testing and will be removed after rendering is complete
    # ffmpeg -r 30 -i %010d.png -vcodec png output.mov
    # beatmap = Beatmap.from_path(r"C:\Users\olegrakov\Desktop\Electronic Boutique - HEXAD (DJPop) [Easy].osu")
    beatmap = Beatmap.from_path(r"C:\Users\olegrakov\Desktop\DJ S3RL - T-T-Techno (feat. Jesskah) (nold_1702) [wkyik's Insane].osu")
    foo = ReplayPlayer(beatmap)

    # rendered_frame = foo.render_frame(50565)
    for index, i in enumerate(range(beatmap.hit_objects[0].time, beatmap.hit_objects[-1:][0].time, 33)):
        # print(index, i)
        foo.render_frame(i).save(fr"C:\Users\olegrakov\Desktop\New folder\{index:010d}.png")
    # ImageShow.show(rendered_frame)
