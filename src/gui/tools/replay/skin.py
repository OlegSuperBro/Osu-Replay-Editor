from __future__ import annotations

from dearpygui import dearpygui as dpg
from os.path import isdir, exists

from typing import List, Tuple, Union

from config import CONSTANTS


class Skin:
    """
    it saves some info and tags for skin elements
    """
    name: str

    default_numbers: List[str]

    approach_circle: str

    cursor: str
    cursor_middle: str
    cursor_smoke: str
    cursor_trail: str

    follow_point: str

    slider_ball: str
    slider_follow_circle: str
    slider_score_point: str
    slider_start_circle: str
    slider_start_circle_overlay: str
    slider_end_circle: str
    slider_end_circle_overlay: str

    hit_miss: str
    hit_50: str
    hit_100: str
    hit_katu: str
    hit_300: str
    hit_geki: str

    hitcircle: str
    hitcircle_overlay: str

    reverse_arrow: str

    @staticmethod
    def load_skin(name: str, prefer2x: bool = True) -> Skin:
        if not isdir(f"{CONSTANTS.skins_dir}\\{name}"):
            raise FileNotFoundError(f"Skin {name} don't exists in 'skins' directory")
        tmp_skin = Skin()

        skin_path = f"{CONSTANTS.skins_dir}\\{name}"

        tmp_skin.name = name

        default_numbers = []
        with dpg.texture_registry():
            for i in range(10):
                _, tag = load_image(skin_path, f"default-{i}", prefer2x)
                default_numbers.append(tag)
            tmp_skin.default_numbers = default_numbers

            _, tag = load_image(skin_path, "cursor", prefer2x)
            tmp_skin.cursor = tag

            _, tag = load_image(skin_path, "cursormiddle", prefer2x)
            tmp_skin.cursor_middle = tag

            _, tag = load_image(skin_path, "cursor-smoke", prefer2x)
            tmp_skin.cursor_smoke = tag

            _, tag = load_image(skin_path, "cursortrail", prefer2x)
            tmp_skin.cursor_trail = tag

            _, tag = load_image(skin_path, "followpoint", prefer2x)
            tmp_skin.follow_point = tag

            _, tag = load_image(skin_path, "sliderb0", prefer2x)
            tmp_skin.slider_ball = tag

            _, tag = load_image(skin_path, "sliderfollowcircle", prefer2x)
            tmp_skin.slider_follow_circle = tag

            _, tag = load_image(skin_path, "sliderscorepoint", prefer2x)
            tmp_skin.slider_score_point = tag

            # _, tag = load_image(skin_path, "slider_start_circle", prefer2x)
            # tmp_skin.slider_start_circle = tag

            # _, tag = load_image(skin_path, "slider_start_circle_overlay", prefer2x)
            # tmp_skin.slider_start_circle_overlay = tag

            # _, tag = load_image(skin_path, "slider_end_circle", prefer2x)
            # tmp_skin.slider_end_circle = tag

            # _, tag = load_image(skin_path, "slider_end_circle_overlay", prefer2x)
            # tmp_skin.slider_end_circle_overlay = tag

            _, tag = load_image(skin_path, "hit0", prefer2x)
            tmp_skin.hit_miss = tag

            _, tag = load_image(skin_path, "hit50", prefer2x)
            tmp_skin.hit_50 = tag

            _, tag = load_image(skin_path, "hit100", prefer2x)
            tmp_skin.hit_100 = tag

            _, tag = load_image(skin_path, "hit100k", prefer2x)
            tmp_skin.hit_katu = tag

            _, tag = load_image(skin_path, "hit300", prefer2x)
            tmp_skin.hit_300 = tag

            _, tag = load_image(skin_path, "hit300g", prefer2x)
            tmp_skin.hit_geki = tag

            _, tag = load_image(skin_path, "hitcircle", prefer2x)
            tmp_skin.hitcircle = tag

            _, tag = load_image(skin_path, "hitcircleoverlay", prefer2x)
            tmp_skin.hitcircle_overlay = tag

            _, tag = load_image(skin_path, "reversearrow", prefer2x)
            tmp_skin.reverse_arrow = tag

        return tmp_skin


def load_image(skin_path, name, prefer2x: bool = True) -> Union[Tuple[str, Tuple[int, int, int, List[int]]], None]:
    """
    load image by name.
    """

    if not prefer2x:
        img = dpg.load_image(f"{skin_path}\\{name}.png")
    elif exists(f"{skin_path}\\{name}@2x.png"):
        img = dpg.load_image(f"{skin_path}\\{name}@2x.png")
    else:
        img = dpg.load_image(f"{skin_path}\\{name}.png")

    tag = f"{name}_texture"
    dpg.add_static_texture(img[0], img[1], img[3], tag=tag)
    return img, tag
