import os, json, logging
import shutil

import colorama

# This handles loading the settings from settings.json
# as well as enabling and/or disabling colored text
# from colorama, and a few utility functions


logging.basicConfig(
    format="%(asctime)s: %(levelname)s - %(module)s - %(funcName)s: %(message)s",
    level=logging.DEBUG,
    filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyMultibound.log"),
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


if not os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")):
    logging.info("settings.json not found, creating it")
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json"), "x") as f:
        json.dump({
            "backup-warning": True,
            "colored-text": True,
            "steamapps-directory": ("c:\\", "Program Files (x86)", "Steam", "steamapps"),
            "compress-profiles": True,
            "use-sbinit": False,
            "starbound": "win64"
        }, f, indent=4)


def load_settings():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")) as f:
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

blank_sbinit = {
  "assetDirectories" : [
    "..\\assets\\",
    "..\\mods\\"
  ],

  "storageDirectory" : "..\\storage\\",

  "defaultConfiguration" : {
    "gameServerBind" : "*",
    "queryServerBind" : "*",
    "rconServerBind" : "*"
  }
}


if not load_settings()["colored-text"]:
    logging.info("Using PlaceHolder instead of colorama")
    Style, Fore, Back = PlaceHolder(), PlaceHolder(), PlaceHolder()
