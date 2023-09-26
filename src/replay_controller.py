from osrparse import Replay

from app_globals import app_globals
from lib.plugin.runner import run_funcs
from lib.errors import NotSupportedExtentionError, CorruptedReplayError, EmptyReplayError, EmptyPathError


def open_replay(path: str):
    if not path or path is None:
        return
    if not path.endswith(".osr"):
        raise NotSupportedExtentionError
    try:
        replay = Replay.from_path(path)
    except Exception as e:
        raise CorruptedReplayError from e

    run_funcs(app_globals.plugin_funcs.on_replay_preload)

    app_globals.replay_path = path
    app_globals.replay = replay

    run_funcs(app_globals.plugin_funcs.on_replay_postload)


def save_replay(path: str):
    if app_globals.replay.game_version == 0:
        raise EmptyReplayError

    if not path:
        raise EmptyPathError

    run_funcs(app_globals.plugin_funcs.on_replay_presave)

    app_globals.replay.write_path(path)
    app_globals.replay_path = path

    run_funcs(app_globals.plugin_funcs.on_replay_postsave)
