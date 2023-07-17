import dearpygui.dearpygui as dpg
from osrparse import Replay
from osrparse.utils import LifeBarState
from typing import List
from dataclasses import dataclass
import utils


@dataclass
class XYPoint:
    x: int
    y: int


class LifeBarGraphWindow:
    def __init__(self) -> None:
        self._id = self._build()

        self.lifebar_graph_list: List[XYPoint] = []

        self.old_x = self.old_y = None
        self.last_point_moved = -1
        self.point_moved = None

    def _build(self) -> None:
        def query(sender, app_data, user_data):
            dpg.set_axis_limits("x_axis", app_data[0], app_data[1])
            dpg.set_axis_limits("y_axis", app_data[2], app_data[3])

        with dpg.item_handler_registry(tag="add_point_click_handler"):
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Right, callback=self.rmb_callback)

        with dpg.tab(label="Life Graph", tag="life_window") as _id:
            with dpg.plot(width=405, height=175, query=True, callback=query, tag="full_life_graph", query_button=dpg.internal_dpg.mvMouseButton_Right):
                dpg.add_plot_axis(dpg.mvXAxis, label="Ticks", tag="full_x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Life %", tag="full_y_axis")
                dpg.set_axis_limits("full_x_axis", 0, 1)
                dpg.set_axis_limits("full_y_axis", -5, 105)
                dpg.add_line_series([], [], parent="full_y_axis", tag="full_life_graph_line")

            with dpg.plot(width=405, height=175, tag="life_graph", context_menu_button=-1, no_title=True):
                dpg.add_plot_axis(dpg.mvXAxis, label="", tag="x_axis", no_tick_labels=True, no_tick_marks=True)
                dpg.add_plot_axis(dpg.mvYAxis, label="", tag="y_axis", no_tick_labels=True, no_tick_marks=True)
                dpg.set_axis_limits("x_axis", 0, 1)
                dpg.set_axis_limits("y_axis", -5, 105)
                dpg.add_line_series([], [], parent="y_axis", tag="life_graph_line")

            dpg.bind_item_handler_registry("life_graph", "add_point_click_handler")

            return _id

    def rmb_callback(self, caller, app_data, user_data) -> None:
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

    def point_callback(self, caller, app_info, user_info):
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

    def load_from_replay(self, replay: Replay):
        lifebar = utils.decrease_lifebar_length(replay.life_bar_graph)
        for _ in range(len(self.lifebar_graph_list) - 1):
            self.delete_last_point_graph()
        self.lifebar_graph_list.clear()

        for index, x, y in zip(range(len(lifebar)), [life_state.time for life_state in lifebar], [int(life_state.life * 100) for life_state in lifebar]):
            self.add_new_point_list(index, x, y)
            self.update_point_plot(index)

        self.update_line_plot()
        dpg.set_axis_limits("full_x_axis", 0, x)
        dpg.set_axis_limits("x_axis", 0, x)

    def update_point_list(self, index: int, x: int, y: int):
        self.lifebar_graph_list[index].x, self.lifebar_graph_list[index].y = x, y

    def add_new_point_list(self, index, x, y):
        self.lifebar_graph_list.insert(index, XYPoint(x, y))

    def delete_point(self, index):
        self.lifebar_graph_list.pop(index)
        self.delete_last_point_graph()

    def delete_last_point_graph(self):
        dpg.delete_item(f"point_{len(self.lifebar_graph_list)}")  # why tf this works?

    def update_all_points(self):
        for index in range(len(self.lifebar_graph_list)):
            self.update_point_plot(index)

    def update_point_plot(self, index):
        dpg.delete_item(f"point_{index}")
        dpg.add_drag_point(parent="life_graph", default_value=(self.lifebar_graph_list[index].x, self.lifebar_graph_list[index].y), label=f"point_{index}", tag=f"point_{index}", callback=self.point_callback)

    def update_line_plot(self):
        if len(self.lifebar_graph_list) >= 2:
            dpg.set_value("full_life_graph_line", [[point.x for point in self.lifebar_graph_list], [point.y for point in self.lifebar_graph_list]])
            dpg.set_value("life_graph_line", [[point.x for point in self.lifebar_graph_list], [point.y for point in self.lifebar_graph_list]])

    def read_in_replay(self, replay: Replay) -> None:
        replay.life_bar_graph = [LifeBarState(int(point.x), round(point.y / 100, 2)) for point in self.lifebar_graph_list]
