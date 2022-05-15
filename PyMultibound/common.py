import logging
import os
import platform
import shutil
import sys
import copy
import json
from os.path import join

logging.basicConfig(
    format="%(asctime)s: %(levelname)s - %(module)s - %(funcName)s: %(message)s",
    level=logging.DEBUG,
    filename=join(os.path.dirname(os.path.realpath(__file__)), "PyMultibound.log"),
    filemode="w"
)

VERSION = "1.0-ALPHA"

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


logging.info(f"PyMultibound Version: {VERSION}, Platform: {platform.system()}")
profilesDir = join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "profiles")  # Directory in which the profiles reside
if platform.system() == "Windows":
    steamappsDir = os.path.join(*["c:\\", "Program Files (x86)", "Steam", "steamapps"])
    starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
    workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
    dumpJson = join(starboundDir, "win32", "dump_versioned_json.exe")  # path to the dump_versioned_json.exe
    makeJson = join(starboundDir, "win32", "make_versioned_json.exe")  # path to the make_versioned_json.exe
    starboundExecutable = join(starboundDir, "win64", "starbound.exe")
    unpackAssets = join(starboundDir, "win64", "asset_unpacker.exe")
    blankSBInit = blankWindowsSBInit

elif platform.system() == "Linux":
    steamappsDir = os.path.join(os.path.expanduser("~/.local/share/Steam/steamapps"))
    starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
    workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
    starboundExecutable = join(starboundDir, "linux", "run-client.sh")
    dumpJson = join(starboundDir, "linux", "dump_versioned_json")  # path to the dump_versioned_json.exe
    makeJson = join(starboundDir, "linux", "make_versioned_json")  # path to the make_versioned_json.exe
    unpackAssets = join(starboundDir, "linux", "asset_unpacker")
    blankSBInit = blankLinuxSBInit

else:
    logging.critical("Unrecognized platform, unable to find steamapps directory")
    sys.exit()

logging.debug("Profile Directory: " + profilesDir)
logging.debug("Starbound Directory: " + starboundDir)
logging.debug("Workshop Directory: " + workshopDir)
logging.debug("Starbound Executable" + starboundExecutable)


def runStarbound(profile: str):
    logging.info("Starting starbound...")
    cmd = f'"{starboundExecutable}" ' \
          f'-bootconfig "{join(profilesDir, profile, "sbinit.config")}"'
    logging.info(f"Launch command: {cmd}")

    if platform.system() == "Windows": os.system(f'"{cmd}"')  # Run the game
    if platform.system() == "Linux": os.system(cmd)  # TODO: find out why windows needs the extra "s
    # Windows crashes without the "s, and linux crashes with them.


def createProfile(name: str, imp: bool) -> bool:
    if os.path.exists(join(profilesDir, name)):
        logging.warning(f"Cannot create profile {name} as it already exists!")
        return False
    logging.info(f"Creating profile with name {name}")
    for option in ["mods", "storage"]:
        directory = join(profilesDir, name, option)
        os.makedirs(directory)
        logging.info(f"Created {directory}")
    with open(join(profilesDir, name, "sbinit.config"), "x") as f:
        sbinit = copy.deepcopy(blankSBInit)
        sbinit["assetDirectories"].append(join(profilesDir, name, "mods"))
        sbinit["storageDirectory"] = join(profilesDir, name, "storage")
        json.dump(sbinit, f, indent=2)
        logging.info(f"Created sbinit.config for {name}")

    if not imp: return True
    # Import steam workshop mods
    if len(next(os.walk(workshopDir))[1]) > 0:
        logging.info(f"Found workshop mods. {name}")
        for modID in next(os.walk(workshopDir))[1]:
            # Basically for numerically id-ed folder
            if not os.path.isfile(join(workshopDir, modID, "contents.pak")):
                logging.warning(f"No contents.pak file was found in workshop mod {modID}")
            else:
                logging.debug("Attempting to extract profile metadata")
                unpacked = unpack(os.path.join(workshopDir, modID, "contents.pak"))
                modData = loadJson(os.path.join(unpacked, "_metadata"))
                ["name"]
                logging.debug("Got mod metadata")
                shutil.rmtree(unpacked)

                safe_move(
                    join(workshopDir, modID, "contents.pak"),
                    join(profilesDir, name, "mods", f"workshop-{modData['name']}-{modData['version']}.pak")
                )
                logging.info(f"Moved workshop mod {modID} ({modData['name']}) to {name}\"s mod folder")


def deleteProfile(name: str) -> bool:
    logging.info(f"Deleting profile {name}")
    try:
        shutil.rmtree(join(profilesDir, name))
        logging.info("Deleted")
        return True
    except Exception as e:
        logging.info(f"Failed to delete: {e}")
        return False


def getProfiles() -> [str]:
    profiles = []
    try:
        for name in next(os.walk(profilesDir))[1]:
            logging.debug(f"Found profile {name}")
            profiles.append(name)
    except StopIteration:
        logging.info("No existing profiles found!")
        pass  # no profiles
    return profiles


def unpack(path: str) -> str:
    logging.info(f"Unpacking {path}")
    command = f'"{unpackAssets}" "{path}" "{path}-unpacked"'
    if platform.system() == "Windows": os.system(f'"{command}"')
    elif platform.system() == "Linux": os.system(command)
    return f"{path}-unpacked"

def loadJson(path: str) -> {}:
    logging.debug(f"Loading json from {path}")
    with open(path, "r") as f:
        raw = f.read()
        raw = raw.replace("inf,", "999999999,")  # FU uses "inf" which is invalid, so replace it with a big number
        # It should automatically overwrite this anyway.
    return json.loads(raw)


def pack(json: str, path:str): pass
