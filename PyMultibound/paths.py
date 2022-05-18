import logging, os, platform, sys, json
from os.path import join
from config import *# Just sets up logging


# About the two sbinits:
# When I switched to Linux I noticed the sbinit.config looked different.
# I'm not sure if this is normal or if its something I did, but I figured I might as
# well put it here.
#
# ...it also crashes without this
blankWindowsSBInit = {
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
blankLinuxSBInit = {
    "assetDirectories": [
        "../assets/",
        "../mods/"
    ],

    "storageDirectory": "../storage/"
}
if platform.system() == "Windows": blankSBInit = blankWindowsSBInit
elif platform.system() == "Linux": blankSBInit = blankLinuxSBInit
else:
    logging.critical("Not running on windows or linux! Cannot run!")
    sys.exit()


def getDefaultPaths():
    # In a function so we don't expose these variables to the global scope,
    # as these are defaults and can be overwritten by the user

    profilesDir = join(os.path.dirname(os.path.realpath(__file__)), os.pardir,
                       "profiles")  # Directory in which the profiles reside
    templatesDir = join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "templates")
    temporaryPath = join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "temp")

    if platform.system() == "Windows":
        steamappsDir = os.path.join(*["c:\\", "Program Files (x86)", "Steam", "steamapps"])

        starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
        workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
        dumpJson = join(starboundDir, "win32", "dump_versioned_json.exe")  # path to the dump_versioned_json.exe
        makeJson = join(starboundDir, "win32", "make_versioned_json.exe")  # path to the make_versioned_json.exe
        starboundExecutable = join(starboundDir, "win64", "starbound.exe")
        unpackAssets = join(starboundDir, "win64", "asset_unpacker.exe")

    elif platform.system() == "Linux":
        steamappsDir = os.path.join(os.path.expanduser("~/.local/share/Steam/steamapps"))

        starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
        workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
        starboundExecutable = join(starboundDir, "linux", "run-client.sh")
        dumpJson = join(starboundDir, "linux", "dump_versioned_json")  # path to the dump_versioned_json.exe
        makeJson = join(starboundDir, "linux", "make_versioned_json")  # path to the make_versioned_json.exe
        unpackAssets = join(starboundDir, "linux", "asset_unpacker")

    else:
        logging.critical("Unrecognized platform, unable to find steamapps directory")
        sys.exit()

    return {
        "workshop": workshopDir,
        "starboundExecutable": starboundExecutable,
        "dumpJson": dumpJson,
        "makeJson": makeJson,
        "unpackAssets": unpackAssets,
        "profiles": profilesDir,
        "templates": templatesDir,
        "temporary": temporaryPath
    }


def savePaths(paths: {}):
    if os.path.exists(settings): os.remove(settings)
    with open(settings, "x") as f:
        json.dump(paths, f, indent=4)


paths = getDefaultPaths()

settings = join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "settings.json")
if not os.path.exists(settings):
    savePaths(paths)
else:
    with open(settings, "r") as f:
        paths = json.load(f)
        logging.info("Loaded settings from file")

if not os.path.exists(paths["profiles"]):
    os.mkdir(paths["profiles"])
    logging.info("Created profiles directory")
if not os.path.exists(paths["templates"]):
    os.mkdir(paths["templates"])
    logging.info("Created templates directory")

logging.info(f"Paths: {paths}")
