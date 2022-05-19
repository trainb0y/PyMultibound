import copy, shutil

from paths import *


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
                modData = getModMetadata(os.path.join(paths['workshop'], modID, "contents.pak"))
                logging.debug("Got mod metadata")

                safe_move(
                    join(paths['workshop'], modID, "contents.pak"),
                    join(paths['profiles'], name, "mods", f"workshop-{modData['name']}-{modData['version']}.pak")
                )
                logging.info(f"Moved workshop mod {modID} ({modData['name']}) to {name}\"s mod folder")


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


def getModMetadata(path: str) -> {}:
    """
    Get the metadata for the mod at path
    """
    unpacked = unpack(path)
    modData = loadJson(os.path.join(unpacked, "_metadata"))
    shutil.rmtree(unpacked)
    return modData


def unpack(path: str) -> str:
    """
    Unpack the .pak file at the given path,
    and return where it was unpacked to.
    """
    logging.debug(f"Attempting to unpack mod at {path}")
    if not path.endswith(".pak"):
        logging.warning(f"Cannot unpack a non .pak file ({path})")
        if os.path.isdir(path):
            logging.warning("It is a directory, assuming it is already unpacked...")
            return path
        else:
            raise FileNotFoundError("Invalid mod file")
    unpackedPath = f"{path}-unpacked"
    if os.path.exists(unpackedPath):
        logging.warning(f"Cannot unpack {path} as it is already unpacked")
        return unpackedPath
    logging.debug(f"Unpacking {path}")
    runCommand(f'"{paths["unpackAssets"]}" "{path}" {unpackedPath}')
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


def createTemplate(characterPath: str) -> bool:
    """
    Make a template from the character at characterPath
    Saves it to templates/<character uuid>.template
    """
    logging.info("Attempting to create a new template")
    character = loadCharacter(characterPath)
    templatePath = join(paths['templates'], f"{character['content']['identity']['name']}.template")
    if os.path.exists(templatePath):
        logging.warning("Could not create template as it would overwrite a template of the same name!")
        return False

    with open(templatePath, "w+") as f:
        json.dump(character["content"]["identity"], f, indent=4)
    logging.info(f"Saved template {templatePath}")
    return True


def loadCharacter(path: str) -> {}:
    """
    Load json from the given .player file at path
    """
    if os.path.exists(paths['temporary']): os.remove(paths['temporary'])
    runCommand(f'"{paths["dumpJson"]}" "{path}" "{paths["temporary"]}"')
    logging.info(f"Created temporary json file from .player at {paths['temporary']}")
    j = loadJson(paths['temporary'])
    os.remove(paths['temporary'])
    return j


def saveCharacter(path: str, data: {}):
    """
    Save the given data to a .player file at path
    """
    with open(paths['temporary'], "w") as f:
        json.dump(data, f, indent=4)
        logging.debug(f"Dumped {data} to the temporary path")
    runCommand(f'"{paths["makeJson"]}" "{paths["temporary"]}" "{path}"')
    logging.info(f"Saved {data} to a character at {path}")


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


def applyTemplate(templatePath: str, characterPath: str, preserveName: bool = False):
    """
    Apply the contents of the template at templatePath
    to the character at characterPath

    preserveName: whether to preserve the character's name
    """
    character = loadCharacter(characterPath)
    with open(templatePath, "r") as f:
        template = json.load(f)
        logging.debug("Loaded template")
    if preserveName:
        template["name"] = character["content"]["identity"]["name"]
        logging.debug("Preserved character name")

    character["content"]["identity"] = template
    logging.info(f"Applied {templatePath} to {characterPath}")
    saveCharacter(characterPath, character)


def getTemplates() -> [(str, str)]:
    """
    Get the file paths of all available templates
    Returns a list of tuples of (name, path)
    """
    logging.debug("Attempting to get a list of templates")
    templates = []
    for template in os.listdir(paths['templates']):
        templates.append((template.replace(".template", ""), join(paths['templates'], template)))
        logging.debug(f"Found character template {template}")
    return templates


def getCharacters() -> [(str, str, str)]:
    """
    Return a list of all characters across all profiles
    Each character entry consists of (path, uuid, name)
    """
    logging.debug("Attempting to get a list of characters")
    characters = []
    try:
        for name in next(os.walk(paths['profiles']))[1]:
            try:
                for character in os.listdir(join(paths['profiles'], name, "storage", "player")):
                    if character.endswith(".player"):
                        path = join(paths['profiles'], name, "storage", "player", character)
                        json = loadCharacter(path)
                        name = json["content"]["identity"]["name"]
                        uuid = json["content"]["uuid"]
                        characters.append((path, uuid, name))
                        logging.debug(f"Found character {name} ({uuid}) at {path}")
            except FileNotFoundError:
                # if the profile exists but contains no players
                logging.warning(f"Player folder not found for {name}")
                logging.warning("This is likely because it does not yet contain any players")
                continue

    except StopIteration:
        logging.info("No existing characters found!")

    return characters


def getModList(profileName: str) -> [{}]:
    """
    Return a list of the given profile's mods' metadata

    Warning: as this has to extract the metadata from the .pak files,
    it may take a while.
    """
    logging.debug(f"Attempting to get mod metadata for profile z{profileName}")
    modList = []
    try:
        modsDir = join(paths['profiles'], profileName, "mods")
        for mod in os.listdir(modsDir):
            modList.append(getModMetadata(join(modsDir, mod)))
    except FileNotFoundError:
        logging.warning(f"Mod folder not found for {profileName}")
        logging.warning("This is likely because it does not yet contain any mods")
        return []

    return modList
