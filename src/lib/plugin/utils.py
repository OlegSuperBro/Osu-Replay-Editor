from aenum import IntEnum

from app_globals import app_globals


class Priority(IntEnum):
    REPLAY_CHANGING = 0
    DEFAULT = 50
    REPLAY_READING = 100


def on_start(priority: int = Priority.DEFAULT):
    def decorator(func):
        app_globals.plugin_funcs.on_start.append((func, priority))
        app_globals.plugin_funcs.on_start.sort(key=lambda x: x[1])
        return func
    return decorator


def on_replay_load(priority: int = Priority.REPLAY_READING):
    def decorator(func):
        app_globals.plugin_funcs.on_replay_load.append((func, priority))
        app_globals.plugin_funcs.on_replay_load.sort(key=lambda x: x[1])
        return func
    return decorator


def on_replay_save(priority: int = Priority.REPLAY_CHANGING):
    def decorator(func):
        app_globals.plugin_funcs.on_replay_save.append((func, priority))
        app_globals.plugin_funcs.on_replay_save.sort(key=lambda x: x[1])
        return func
    return decorator


def on_data_update(priority: int = Priority.DEFAULT):
    def decorator(func):
        app_globals.plugin_funcs.on_data_update.append((func, priority))
        app_globals.plugin_funcs.on_data_update.sort(key=lambda x: x[1])
        return func
    return decorator


def on_frame_update(priority: int = Priority.DEFAULT):
    def decorator(func):
        app_globals.plugin_funcs.on_frame_update.append((func, priority))
        app_globals.plugin_funcs.on_frame_update.sort(key=lambda x: x[1])
        return func
    return decorator


def on_window_build(priority: int = Priority.DEFAULT):
    def decorator(func):
        app_globals.plugin_funcs.on_window_build.append((func, priority))
        app_globals.plugin_funcs.on_window_build.sort(key=lambda x: x[1])
        return func
    return decorator
