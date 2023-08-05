from typing import List
from pyosutools.datatypes import BeatmapDB


def get_beatmap_by_hash(beatmaps: List[BeatmapDB], beatmap_hash: str) -> BeatmapDB:
    return next(
        (beatmap for beatmap in beatmaps if beatmap_hash == beatmap.md5_hash),
        None,
    )
