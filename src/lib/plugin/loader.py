import importlib
import pkgutil

import plugins


def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def get_plugins():
    return {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(plugins)
    }
