from __future__ import annotations

from dearpygui import dearpygui as dpg
from os.path import isdir, exists
from pathlib import Path

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
    reverse_arrow: str

    hit_miss: str
    hit_50: str
    hit_100: str
    hit_katu: str
    hit_300: str
    hit_geki: str

    hitcircle: str
    hitcircle_overlay: str


    @staticmethod
    def load_skin(name: str, fallback_skin: str = None, prefer2x: bool = True) -> Skin:
        if not isdir(f"{CONSTANTS.skins_dir}\\{name}"):
            raise FileNotFoundError(f"Skin {name} don't exists in 'skins' directory")

        def load_with_fallback(image_name):
            if exists(skin_path / image_name):
                _, tag = load_image(skin_path, image_name, prefer2x)
            else:
                _, tag = load_image(fallback_skin_path, image_name, prefer2x)
            return tag

        tmp_skin = Skin()

        skin_path = Path(f"{CONSTANTS.skins_dir}\\{name}")

        fallback_skin_path = CONSTANTS.default_skin_path
        if fallback_skin is not None:
            fallback_skin_path = f"{CONSTANTS.skins_dir}\\{fallback_skin}"

        tmp_skin.name = name

        default_numbers = []
        with dpg.texture_registry():
            for i in range(10):
                default_numbers.append(load_with_fallback(f"default-{i}"))
            tmp_skin.default_numbers = default_numbers

            tmp_skin.cursor = load_with_fallback("cursor")
            tmp_skin.cursor_middle = load_with_fallback("cursormiddle")
            tmp_skin.cursor_smoke = load_with_fallback("cursor-smoke")
            tmp_skin.cursor_trail = load_with_fallback("cursortrail")

            tmp_skin.follow_point = load_with_fallback("followpoint")

            tmp_skin.slider_ball = load_with_fallback("sliderb0")
            tmp_skin.slider_follow_circle = load_with_fallback("sliderfollowcircle")
            tmp_skin.slider_score_point = load_with_fallback("sliderscorepoint")
            tmp_skin.slider_start_circle = load_with_fallback("sliderstartcircle")
            tmp_skin.slider_start_circle_overlay = load_with_fallback("sliderstartcircleoverlay")
            tmp_skin.slider_end_circle = load_with_fallback("sliderendcircle")
            tmp_skin.slider_end_circle_overlay = load_with_fallback("sliderendcircleoverlay")
            tmp_skin.reverse_arrow = load_with_fallback("reversearrow")

            tmp_skin.hit_miss = load_with_fallback("hit0")
            tmp_skin.hit_50 = load_with_fallback("hit50")
            tmp_skin.hit_100 = load_with_fallback("hit100")
            tmp_skin.hit_katu = load_with_fallback("hit100k")
            tmp_skin.hit_300 = load_with_fallback("hit300")
            tmp_skin.hit_geki = load_with_fallback("hit300g")

            tmp_skin.hitcircle = load_with_fallback("hitcircle")
            tmp_skin.hitcircle_overlay = load_with_fallback("hitcircleoverlay")

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
    try:
        dpg.add_static_texture(img[0], img[1], img[3], tag=tag)
    except TypeError:
        raise FileNotFoundError(f"File {name} not found in {skin_path} skin")
    return img, tag
