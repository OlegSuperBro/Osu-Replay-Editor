import inspect
import logging
from typing import List, Callable

from app_globals import app_globals
from config import CONSTANTS
import lib.plugin.var_types as var_types


class PluginError(Exception):
    ...


class AnnotationError(PluginError):
    ...


def check_func(func):
    spec = inspect.getfullargspec(func)
    for arg in spec.args:
        if arg not in spec.annotations.keys():
            raise AnnotationError(f"Argument \"{arg}\" should have annotation")

    for arg, annotation in spec.annotations.items():
        if annotation not in var_types._get_all():
            raise AnnotationError(f"Argument \"{arg}\" have invalid annotaion \"{annotation}\"")


def run_funcs(funcs: List[Callable]):
    for func, _ in funcs:
        try:
            check_func(func)
        except PluginError as e:
            logging.warning(f"{func} encountered an error: {e}")
            continue

        kwargs = {}

        for arg, annotation in inspect.get_annotations(func).items():
            if annotation is var_types.MainWindow:
                kwargs[arg] = CONSTANTS.TAGS.main_window

            elif annotation is var_types.TabBar:
                kwargs[arg] = CONSTANTS.TAGS.tab_bar

            elif annotation is var_types.Replay:
                kwargs[arg] = app_globals.replay

            elif annotation is var_types.ReplayPath:
                kwargs[arg] = app_globals.replay_path

            elif annotation is var_types.Osudb:
                kwargs[arg] = app_globals.osu_db

            elif annotation is var_types.UpdateFunc:
                kwargs[arg] = app_globals.data_update_func

        func(**kwargs)
