from aenum import IntEnum
from typing import List

from app_globals import app_globals


class Priority(IntEnum):
    REPLAY_CHANGING = 0
    DEFAULT = 50
    REPLAY_READING = 100


def _create_decorator(funcs_list: List, default_priority: int):
    def decorator(priority: int = default_priority):
        def sub_decorator(func):
            funcs_list.append((func, priority))
            funcs_list.sort(key=lambda x: x[1])
            return func
        return sub_decorator
    return decorator


on_start = _create_decorator(app_globals.plugin_funcs.on_start, Priority.DEFAULT)
on_replay_preload = _create_decorator(app_globals.plugin_funcs.on_replay_preload, Priority.REPLAY_READING)
on_replay_postload = _create_decorator(app_globals.plugin_funcs.on_replay_postload, Priority.REPLAY_READING)
on_replay_presave = _create_decorator(app_globals.plugin_funcs.on_replay_presave, Priority.REPLAY_CHANGING)
on_replay_postsave = _create_decorator(app_globals.plugin_funcs.on_replay_postsave, Priority.REPLAY_CHANGING)
on_data_update = _create_decorator(app_globals.plugin_funcs.on_data_update, Priority.DEFAULT)
on_frame_update = _create_decorator(app_globals.plugin_funcs.on_frame_update, Priority.DEFAULT)
on_window_build = _create_decorator(app_globals.plugin_funcs.on_window_build, Priority.DEFAULT)
