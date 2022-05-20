import copy
import json
import logging
import os
import shutil
from os.path import join

from PyMultibound.common.paths import blankSBInit, paths
from PyMultibound.common.util import loadJson, safe_move, unpack


def deleteProfile(name: str) -> bool:
    """
    Delete the profile with the given name
    """
    logging.info(f"Deleting profile {name}")
    try:
        shutil.rmtree(join(paths['profiles'], name))
        logging.info("Deleted")
        return True
    except Exception as e:
        logging.info(f"Failed to delete: {e}")
        return False


def getProfiles() -> [str]:
    """
    Get the names of every known profile
    """
    profiles = []
    try:
        for name in next(os.walk(paths['profiles']))[1]:
            logging.debug(f"Found profile {name}")
            profiles.append(name)
    except StopIteration:
        logging.info("No existing profiles found!")
        pass  # no profiles
    return profiles


def createProfile(name: str, imp: bool) -> bool:
    """
    Create a blank profile with the given name.

    imp: whether to import subscribed Steam Workshop mods
    """
    if os.path.exists(join(paths["profiles"], name)):
        logging.warning(f"Cannot create profile {name} as it already exists!")
        return False
    logging.info(f"Creating profile with name {name}")
    for option in ["mods", "storage"]:
        directory = join(paths['profiles'], name, option)
        os.makedirs(directory)
        logging.info(f"Created {directory}")
    with open(join(paths['profiles'], name, "sbinit.config"), "x") as f:
        sbinit = copy.deepcopy(blankSBInit)
        sbinit["assetDirectories"].append(join(paths['profiles'], name, "mods"))
        sbinit["storageDirectory"] = join(paths['profiles'], name, "storage")
        json.dump(sbinit, f, indent=2)
        logging.info(f"Created sbinit.config for {name}")

    if not imp: return True
    # Import steam workshop mods
    if len(next(os.walk(paths['workshop']))[1]) > 0:
        logging.info(f"Found workshop mods. {name}")
        for modID in next(os.walk(paths['workshop']))[1]:
            # Basically for numerically id-ed folder
            if not os.path.isfile(join(paths['workshop'], modID, "contents.pak")):
                logging.warning(f"No contents.pak file was found in workshop mod {modID}")
            else:
                logging.debug("Attempting to extract profile metadata")
                unpacked = unpack(os.path.join(paths['workshop'], modID, "contents.pak"))
                modData = loadJson(os.path.join(unpacked, "_metadata"))
                logging.debug("Got mod metadata")
                shutil.rmtree(unpacked)

                safe_move(
                    join(paths['workshop'], modID, "contents.pak"),
                    join(paths['profiles'], name, "mods", f"workshop-{modData['name']}-{modData['version']}.pak")
                )
                logging.info(f"Moved workshop mod {modID} ({modData['name']}) to {name}\"s mod folder")
