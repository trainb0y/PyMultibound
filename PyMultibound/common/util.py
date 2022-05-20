import json
import logging
import os
import platform
import shutil
from os.path import join

from PyMultibound.common.paths import paths


def safe_move(src, dst):
    """
    Attempt to move a directory or file using shutil.move()
    Returns true if it worked, false otherwise.
    """
    logging.debug(f"Moving {src} to {dst}")
    try:
        shutil.move(src, dst)
        return True
    except Exception as e:
        logging.error(f"An error occurred while trying to move {src} to {dst}: {e}")
        return False


def runStarbound(profile: str):
    """
    Run Starbound with the given profile
    """
    logging.info("Starting Starbound...")
    cmd = f'"{paths["starboundExecutable"]}" ' \
          f'-bootconfig "{join(paths["profiles"], profile, "sbinit.config")}"'
    logging.info(f"Launch command: {cmd}")
    runCommand(cmd)
    logging.info("Starbound stopped")


def unpack(path: str) -> str:
    """
    Unpack the .pak file at the given path,
    and save it to <path>-unpacked/
    """
    logging.debug(f"Unpacking {path}")
    runCommand(f'"{paths["unpackAssets"]}" "{path}" "{path}-unpacked"')
    logging.debug("Unpacked")
    return f"{path}-unpacked"


def loadJson(path: str) -> {}:
    """
    Load the json at the given path
    Automatically replaces some invalid json
    (FU's "inf" with a large integer, etc.)
    """
    logging.debug(f"Loading json from {path}")
    with open(path, "r") as f:
        raw = f.read()
        raw = raw.replace("inf,", "999999999,")  # FU uses "inf" which is invalid, so replace it with a big number
        # It should automatically overwrite this anyway.
    return json.loads(raw)


def runCommand(command: str):
    """
    Run the specified command.
    Uses os.system() but formats the command depending on current platform
    """
    # Windows crashes without the "s, and linux crashes with them.
    if platform.system() == "Windows":
        os.system(f'"{command}"')
    elif platform.system() == "Linux":
        os.system(command)
    else:
        logging.critical(f"Not on Windows or Linux ({platform.system()})")
