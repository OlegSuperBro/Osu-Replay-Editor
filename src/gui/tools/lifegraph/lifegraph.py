import dearpygui.dearpygui as dpg
from osrparse import Replay
from osrparse.utils import LifeBarState
from typing import List
from dataclasses import dataclass
import utils

from gui.template import Template
from config import CONSTANTS


@dataclass
class XYPoint:
    x: int
    y: int


class LifeBarGraphTab(Template):
    preview_offset_x = -410
    preview_offset_y = -20
    squish = 100
    # 415x175. Full screen is 4 times wider and 6 time taller

    def __init__(self, update_func) -> None:
        self._id = self._build()

        self.lifebar_graph_list: List[XYPoint] = []

        self.old_x = self.old_y = None
        self.last_point_moved = -1
        self.point_moved = None

    def _build(self) -> None:
        with dpg.texture_registry():
            img = dpg.load_image(f"{CONSTANTS.assets_dir}/song_result_screen.jpg")
            dpg.add_dynamic_texture(img[0], img[1], img[3], tag="preview_result_screen")

        with dpg.item_handler_registry(tag="add_point_click_handler"):
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Right, callback=self.rmb_callback)

        with dpg.tab(label="Life Graph", tag="life_window") as _id:
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label="Save Mode", default_value=True, tag="save_mode_toggle", callback=self.toggle_save_mode)
                dpg.add_spacer(width=50)

                with dpg.group(horizontal=True, tag="save_mode_group"):
                    pass
                with dpg.group(horizontal=True, show=False, tag="unsave_mode_group"):
                    dpg.add_checkbox(label="Show Preview", callback=lambda x: dpg.configure_item("preview_lifebar", show=dpg.get_value(x)))

            with dpg.plot(width=-1, height=-1, tag="life_graph", context_menu_button=-1, no_title=True):
                dpg.add_plot_axis(dpg.mvXAxis, label="", tag="x_axis", no_tick_labels=True, no_tick_marks=True)
                dpg.add_plot_axis(dpg.mvYAxis, label="", tag="y_axis", no_tick_labels=True, no_tick_marks=True)

                with dpg.draw_layer(tag="unsave_group", show=False):
                    dpg.add_image_series("preview_result_screen", (0, self.preview_offset_y), (0, 600 + self.preview_offset_y), parent="x_axis", tag="preview_lifebar", show=False)
                    dpg.draw_rectangle(pmin=(0, 0), pmax=(0, 100), color=(255, 0, 0, 255), thickness=20, tag="save_zone_square")

                dpg.add_line_series([], [], parent="y_axis", tag="life_graph_line")

            dpg.bind_item_handler_registry("life_graph", "add_point_click_handler")

            return _id

    def rmb_callback(self, caller=None, app_data=None, user_data=None) -> None:
        x, y = dpg.get_plot_mouse_pos()

        if x != self.old_x or y != self.old_y:
            self.point_moved = False
            self.old_x = x
            self.old_y = y

        if self.point_moved:
            self.delete_point(self.last_point_moved)
        else:
            for index, point in enumerate(self.lifebar_graph_list):
                if abs(point.x - x) < dpg.get_axis_limits("x_axis")[1] / 100 * 2 and abs(point.y - y) < 3:
                    self.delete_point(index)
                    break
            else:
                self.add_new_point_list(len(self.lifebar_graph_list), x, y)
        self.update_all_points()
        self.update_line_plot()

    def point_callback(self, caller, app_info=None, user_info=None):
        index = int(dpg.get_item_alias(caller).split("_")[1])
        x, y, _, _ = dpg.get_value(caller)

        self.last_point_moved = index
        self.point_moved = True

        mouse_x, mouse_y = dpg.get_plot_mouse_pos()
        if mouse_x != self.old_x or mouse_y != self.old_y:
            self.old_x = mouse_x
            self.old_y = mouse_y

        self.update_point_list(index, x, y)
        self.update_line_plot()

    def toggle_save_mode(self, caller=None, app_info=None, user_info=None):
        dpg.configure_item("save_mode_group", show=dpg.get_value("save_mode_toggle"))
        dpg.configure_item("unsave_mode_group", show=not dpg.get_value("save_mode_toggle"))
        dpg.configure_item("unsave_group", show=not dpg.get_value("save_mode_toggle"))

    def update_preview(self):
        dpg.configure_item("save_zone_square", pmin=(0, 0), pmax=(self.lifebar_graph_list[-1:][0].x, 100))

        dpg.configure_item("preview_lifebar",
                           bounds_min=((self.lifebar_graph_list[-1:][0].x / 415 * (self.preview_offset_x + self.squish / 2)), self.preview_offset_y),
                           bounds_max=((self.lifebar_graph_list[-1:][0].x / 415 * (1980 + self.preview_offset_x - self.squish / 2)), 600 + self.preview_offset_y))

    def read_from_replay(self, replay: Replay):
        lifebar = utils.decrease_lifebar_length(replay.life_bar_graph)
        for _ in range(len(self.lifebar_graph_list) - 1):
            self.delete_last_point_graph()
        self.lifebar_graph_list.clear()

        for index, x, y in zip(range(len(lifebar)), [life_state.time for life_state in lifebar], [int(life_state.life * 100) for life_state in lifebar]):
            self.add_new_point_list(index, x, y)
            self.update_point_plot(index)

        self.update_line_plot()
        self.update_preview()

    def update_point_list(self, index: int, x: int, y: int):
        self.lifebar_graph_list[index].x, self.lifebar_graph_list[index].y = x, y

    def add_new_point_list(self, index, x, y):
        self.lifebar_graph_list.insert(index, XYPoint(x, y))

    def delete_point(self, index):
        self.lifebar_graph_list.pop(index)
        self.delete_last_point_graph()

    def delete_last_point_graph(self):
        dpg.delete_item(f"point_{len(self.lifebar_graph_list)}")

    def update_all_points(self):
        for index in range(len(self.lifebar_graph_list)):
            self.update_point_plot(index)

    def update_point_plot(self, index):
        dpg.delete_item(f"point_{index}")
        dpg.add_drag_point(parent="life_graph", default_value=(self.lifebar_graph_list[index].x, self.lifebar_graph_list[index].y), label=f"point_{index}", tag=f"point_{index}", callback=self.point_callback)

    def update_line_plot(self):
        if len(self.lifebar_graph_list) >= 2:
            dpg.set_value("life_graph_line", [[point.x for point in self.lifebar_graph_list], [point.y for point in self.lifebar_graph_list]])

    def read_in_replay(self, replay: Replay) -> None:
        replay.life_bar_graph = [LifeBarState(int(point.x), round(point.y / 100, 2)) for point in self.lifebar_graph_list]
