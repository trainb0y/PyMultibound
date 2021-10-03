import json
import logging
import os
import platform
import shutil
from os.path import join

import colorama

# This handles loading the settings from settings.json
# as well as enabling and/or disabling colored text
# from colorama, and a few utility functions


logging.basicConfig(
    format="%(asctime)s: %(levelname)s - %(module)s - %(funcName)s: %(message)s",
    level=logging.DEBUG,
    filename=join(os.path.dirname(os.path.realpath(__file__)), "PyMultibound.log"),
    filemode="w"
)


class PlaceHolder:  # There has GOT to be a better way to do this
    """
    A placeholder class to replace colorama codes with.
    The entire idea of having to make this just rubs me the wrong
    way.
    """

    def __init__(self):
        self.BLACK, self.RED, self.GREEN, self.YELLOW = "", "", "", ""
        self.BLUE, self.MAGENTA, self.CYAN, self.WHITE, self.RESET = "", "", "", "", ""
        self.DIM, self.NORMAL, self.BRIGHT, self.RESET_ALL = "", "", "", ""


if not os.path.isfile(join(os.path.dirname(os.path.realpath(__file__)), "settings.json")):
    logging.info("settings.json not found, creating it")
    with open(join(os.path.dirname(os.path.realpath(__file__)), "settings.json"), "x") as f:
        json.dump({
            "colored-text": True,
            "steamapps-directory": ("c:\\", "Program Files (x86)", "Steam", "steamapps"),
            "compress-profiles": True,
        }, f, indent=4)


def load_settings():
    with open(join(os.path.dirname(os.path.realpath(__file__)), "settings.json")) as f:
        settings = json.load(f)
        logging.info("Got settings from settings.json")
        return settings


def safe_move(src, dst):
    """
    Attempt to move a directory or file using shutil.move()
    Returns true if it worked, false otherwise.
    """
    try:
        shutil.move(src, dst)
        return True
    except Exception as e:
        logging.error(f"An error occured while trying to move {src} to {dst}: {e}")
        return False


colorama.init(autoreset=True)
Style, Fore, Back = colorama.Style, colorama.Fore, colorama.Back

# About the two sbinits:
# When I switched to Linux I noticed the sbinit.config looked different.
# I'm not sure if this is normal or if its something I did, but I figured I might as
# well put it here.
#
# ...it also crashes without this
blank_sbinit_windows = {
    "assetDirectories": [
        "..\\assets\\",
        "..\\mods\\"
    ],

    "storageDirectory": "..\\storage\\",

    "defaultConfiguration": {
        "gameServerBind": "*",
        "queryServerBind": "*",
        "rconServerBind": "*"
    }
}
blank_sbinit_linux = {
    "assetDirectories": [
        "../assets/",
        "../mods/"
    ],

    "storageDirectory": "../storage/"
}

settings = load_settings()
if not settings["colored-text"]:
    logging.info("Using PlaceHolder instead of colorama")
    Style, Fore, Back = PlaceHolder(), PlaceHolder(), PlaceHolder()

# Find all of the directories
profiles_dir = join(os.path.dirname(os.path.realpath(__file__)),
                            "profiles")  # Directory in which the profiles reside
steamapps_dir = join(
    *settings["steamapps-directory"])  # see docs on os.path.join          # Directory for all steam apps ("steamapps")
starbound_dir = join(steamapps_dir, "common", "Starbound")  # Main Starbound directory inside of steamapps
workshop_dir = join(steamapps_dir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
temp_dir = join(os.path.dirname(os.path.realpath(__file__)), "temp")  # Directory to store temporary files in
templates_dir = join(os.path.dirname(os.path.realpath(__file__)),
                             "templates")  # Directory to store appearance templates in

if platform.system() == "Linux":
    asset_pack_tools_dir = join(starbound_dir, "linux")
    starbound_executable = join(starbound_dir, "linux", "run-client.sh")
    dump_json = join(starbound_dir, "linux", "dump_versioned_json")  # path to the dump_versioned_json.exe
    make_json = join(starbound_dir, "linux", "make_versioned_json")  # path to the make_versioned_json.exe
    blank_sbinit = blank_sbinit_linux

elif platform.system() == "Windows":
    dump_json = join(starbound_dir, "win32", "dump_versioned_json.exe")  # path to the dump_versioned_json.exe
    make_json = join(starbound_dir, "win32", "make_versioned_json.exe")  # path to the make_versioned_json.exe
    starbound_executable = join(starbound_dir, "win64", "starbound.exe")
    blank_sbinit = blank_sbinit_windows

for directory in [temp_dir, templates_dir, profiles_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory for {directory}")
