import importlib
import pkgutil

from config import CONSTANTS


def iter_namespace(path):
    return pkgutil.iter_modules(path, "plugins" + ".")


def get_plugins():
    return {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace([CONSTANTS.PATHS.plugin_dir])
    }
