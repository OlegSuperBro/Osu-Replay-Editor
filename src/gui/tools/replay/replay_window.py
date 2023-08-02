from dearpygui import dearpygui as dpg
from osrparse import Replay
from pyosutools.beatmaps.beatmap import Beatmap
from pyosutools.db.osu import Osudb
from pathlib import Path

from gui.template import TabTemplate
from config import CONFIG

from .beatmap_render import BeatmapRender
from .replay_render import ReplayRender
from .skin import Skin
from .utils import update_replay_data

class ReplayPlayer(TabTemplate):
    def __init__(self, update_func) -> None:
        self._id = self._build()
        self.beatmap = None
        self.replay = None
        self.replay_data = None
        self.current_tick = 50000

    def _build(self) -> int:
        with dpg.tab(label="Replay Editor", tag="replay_window") as _id:
            with dpg.group():
                self.frame = dpg.add_drawlist(640, 480)
                skin = Skin.load_skin("Default")
                self.beatmap_renderer = BeatmapRender(skin, self.frame)
                self.replay_renderer = ReplayRender(skin, self.frame)
            with dpg.group():
                dpg.add_text("TIMELINE")
            return _id

    def update(self, db: Osudb, replay: Replay) -> None:
        self.render_frame(self.current_tick)

    def on_replay_load(self, db: Osudb, replay: Replay) -> None:
        db_map = db.get_beatmap_from_hash(replay.beatmap_hash)
        self.beatmap = Beatmap.from_path(Path(CONFIG.osu_path) / "Songs" / Path(db_map.folder_name) / Path(db_map.osu_file))

        self.replay = replay

        self.replay_data = update_replay_data(self.replay.replay_data)

    def render_frame(self, timestamp: int):
        dpg.delete_item(self.frame, children_only=True)

        dpg.draw_rectangle((0, 0), (640, 480), color=(0, 0, 0, 255), fill=(0, 0, 0, 255), parent=self.frame)

        if self.current_tick > self.beatmap.hit_objects[-1:][0].time:
            self.current_tick = 0

        self.beatmap_renderer.render_frame(self.beatmap, self.current_tick)
        self.replay_renderer.render_frame(self.replay_data, self.current_tick)

        self.current_tick += 33
