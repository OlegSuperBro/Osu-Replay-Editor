import dearpygui.dearpygui as dpg
from osrparse import Replay

import utils


class LifeBarGraphWindow:
    def __init__(self) -> None:
        self._build()

        self.lifebar_graph_dict = {}

    def _build(self) -> None:
        def query(sender, app_data, user_data):
            dpg.set_axis_limits("x_axis", app_data[0], app_data[1])
            dpg.set_axis_limits("y_axis", app_data[2], app_data[3])

        with dpg.window(label="Life Graph", pos=(0, 400), min_size=(420, 400), max_size=(420, 400), tag="life_window", on_close=lambda: dpg.delete_item("life_window"), no_scrollbar=True):
            with dpg.plot(width=405, height=175, query=True, callback=query, tag="full_life_graph", query_button=dpg.internal_dpg.mvMouseButton_Right):
                dpg.add_plot_axis(dpg.mvXAxis, label="Ticks", tag="full_x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Life", tag="full_y_axis")
                dpg.set_axis_limits("full_x_axis", 0, 1)
                dpg.set_axis_limits("full_y_axis", -5, 105)

            with dpg.plot(width=405, height=175, tag="life_graph", context_menu_button=-1):
                dpg.add_plot_axis(dpg.mvXAxis, label="Ticks", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Life", tag="y_axis")
                dpg.set_axis_limits("x_axis", 0, 1)
                dpg.set_axis_limits("y_axis", -5, 105)

    def load_from_replay(self, replay: Replay):
        lifebar = utils.decrease_lifebar_length(replay.life_bar_graph)
        self.lifebar_graph_dict.clear()

        if not dpg.does_item_exist("full_life_graph_line"):
            dpg.add_line_series([], [], parent="full_y_axis", tag="full_life_graph_line")
        if not dpg.does_item_exist("life_graph_line"):
            dpg.add_line_series([], [], parent="y_axis", tag="life_graph_line")

        for index, x, y in zip(range(len(lifebar)), [life_state.time for life_state in lifebar], [int(life_state.life * 100) for life_state in lifebar]):
            dpg.delete_item(f"point_{index}")
            self.change_lifebar_dict(f"point_{index}", x, y)
            dpg.add_drag_point(parent="life_graph", default_value=(x, y), label=f"point_{index}", tag=f"point_{index}", callback=lambda x, y: self.change_lifebar_dict(dpg.get_item_alias(x), dpg.get_value(x)[0], dpg.get_value(x)[1]))

        dpg.set_axis_limits("full_x_axis", 0, x)
        dpg.set_axis_limits("x_axis", 0, x)

    def change_lifebar_dict(self, label, x, y):
        if y > 100:
            y = 100
            dpg.delete_item(label)
            dpg.add_drag_point(parent="life_graph", default_value=(x, y), label=label, tag=label, callback=lambda x, y: self.change_lifebar_dict(dpg.get_item_alias(x), dpg.get_value(x)[0], dpg.get_value(x)[1]))

        self.lifebar_graph_dict[label] = {"x": x, "y": y / 100}

        dpg.set_value("full_life_graph_line", [[value.get("x") for value in self.lifebar_graph_dict.values()], [value.get("y") * 100 for value in self.lifebar_graph_dict.values()]])
        dpg.set_value("life_graph_line", [[value.get("x") for value in self.lifebar_graph_dict.values()], [value.get("y") * 100 for value in self.lifebar_graph_dict.values()]])

    def read_in_replay(self, replay) -> Replay:
        pass
