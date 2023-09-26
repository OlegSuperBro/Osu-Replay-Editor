from os import mkdir, PathLike
from os.path import dirname, exists, isdir
from pyosutools.database import Osudb

from config import CONSTANTS


def get_osu_db_cached(db_path: PathLike) -> Osudb:
    cache_path = f"{CONSTANTS.PATHS.cache_dir}/beatmaps_cache.pickle"
    if not isdir(dirname(cache_path)):
        mkdir(dirname(cache_path))

    if exists(cache_path):
        tmp = Osudb.from_path(db_path, skip_beatmaps=True)
        tmp.load_cache_beatmaps(cache_path)
        return tmp

    return Osudb.from_path(db_path)


def save_osu_db_cache(osudb: Osudb) -> None:
    cache_path = f"{CONSTANTS.PATHS.cache_dir}/beatmaps_cache.pickle"
    if not isdir(dirname(cache_path)):
        mkdir(dirname(cache_path))
    osudb.save_cache_beatmaps(cache_path)
