import importlib
import pkgutil
import ast
from typing import List
from os import PathLike

from config import CONSTANTS


def iter_namespace(path):
    return pkgutil.iter_modules(path, "plugins" + ".")


def get_plugins():
    return {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace([CONSTANTS.PATHS.plugin_dir])
    }


def get_vars_without_load(file_path: PathLike):
    plugin_file = open(file_path)
    plugin_content = plugin_file.read()
    dump = ast.parse(plugin_content)
    lines: List[ast.Assign] = list(filter(lambda x: isinstance(x, ast.Assign), ast.iter_child_nodes(dump)))

    result = {}
    for line in lines:
        if isinstance(line.value, ast.List):
            values = [const.value for const in line.value.elts]
        else:
            values = line.value.value
        result[line.targets[0].id] = values
    return result


def get_plugin_info():
    plugin_info = {}
    plugins = [(name, ispkg) for finder, name, ispkg in iter_namespace([CONSTANTS.PATHS.plugin_dir])]
    for plugin, ispkg in plugins:
        plugin_path_name = plugin.replace("plugins.", "")

        if ispkg:
            plugin_path = CONSTANTS.PATHS.program_path + f"/{'/'.join(plugin.split('.'))}/__init__.py"
        else:
            plugin_path = CONSTANTS.PATHS.program_path + f"/{plugin.replace('.', '/')}.py"
        variables = get_vars_without_load(plugin_path)

        plugin_info[plugin_path_name] = {}

        if variables.get("NAME") is not None:
            plugin_info[plugin_path_name]["name"] = variables.get("NAME")
        else:
            plugin_info[plugin_path_name]["name"] = plugin_path_name

        if variables.get("AUTHOR") is not None:
            plugin_info[plugin_path_name]["author"] = variables.get("AUTHOR")
        else:
            plugin_info[plugin_path_name]["author"] = "Unknown"

        if variables.get("REQUIREMENTS") is not None:
            plugin_info[plugin_path_name]["requirements"] = variables.get("REQUIREMENTS")
        else:
            plugin_info[plugin_path_name]["requirements"] = []

        if variables.get("DESCRIPTION") is not None:
            plugin_info[plugin_path_name]["description"] = variables.get("DESCRIPTION")
        else:
            plugin_info[plugin_path_name]["description"] = "Description not profided"

    return plugin_info
