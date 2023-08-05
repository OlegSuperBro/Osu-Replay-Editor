from osrparse import Replay
from pyosutools.database import Osudb

from typing import Callable


class TabTemplate:
    def __init__(self, update_func: Callable) -> None:
        ...

    def update(self, db: Osudb, replay: Replay) -> None:
        ...

    def on_replay_load(self, db: Osudb, replay: Replay) -> None:
        ...

    def read_from_replay(self, replay: Replay) -> None:
        ...

    def read_in_replay(self, replay: Replay) -> None:
        ...
