import sys
import subprocess

from lib.plugin.loader import get_plugin_info
from config import CONSTANTS


def install_requirement(req: str):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-q", "--target", CONSTANTS.site_packages_folder, req])


def install_all_plugins_requirements():
    for name, info in get_plugin_info().items():
        if info.get("requirements") is None:
            continue
        for requirement in info.get("requirements"):
            install_requirement(requirement)
