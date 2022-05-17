import copy
import json
import shutil

from paths import *

logging.basicConfig(
    format="%(asctime)s: %(levelname)s - %(module)s - %(funcName)s: %(message)s",
    level=logging.DEBUG,
    filename=join(os.path.dirname(os.path.realpath(__file__)), "PyMultibound.log"),
    filemode="w"
)

VERSION = "v1.0.1"

logging.info(f"PyMultibound Version: {VERSION}, Platform: {platform.system()}")
logging.debug("Profile Directory: " + profilesDir)
logging.debug("Workshop Directory: " + workshopDir)
logging.debug("Starbound Executable" + starboundExecutable)


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
        logging.error(f"An error occured while trying to move {src} to {dst}: {e}")
        return False


def runStarbound(profile: str):
    """
    Run Starbound with the given profile
    """
    logging.info("Starting starbound...")
    cmd = f'"{starboundExecutable}" ' \
          f'-bootconfig "{join(profilesDir, profile, "sbinit.config")}"'
    logging.info(f"Launch command: {cmd}")
    runCommand(cmd)
    logging.info("Starbound stopped")


def createProfile(name: str, imp: bool) -> bool:
    """
    Create a blank profile with the given name.

    imp: whether to import subscribed Steam Workshop mods
    """
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
                logging.debug("Got mod metadata")
                shutil.rmtree(unpacked)

                safe_move(
                    join(workshopDir, modID, "contents.pak"),
                    join(profilesDir, name, "mods", f"workshop-{modData['name']}-{modData['version']}.pak")
                )
                logging.info(f"Moved workshop mod {modID} ({modData['name']}) to {name}\"s mod folder")


def deleteProfile(name: str) -> bool:
    """
    Delete the profile with the given name
    """
    logging.info(f"Deleting profile {name}")
    try:
        shutil.rmtree(join(profilesDir, name))
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
        for name in next(os.walk(profilesDir))[1]:
            logging.debug(f"Found profile {name}")
            profiles.append(name)
    except StopIteration:
        logging.info("No existing profiles found!")
        pass  # no profiles
    return profiles


def unpack(path: str) -> str:
    """
    Unpack the .pak file at the given path,
    and save it to <path>-unpacked/
    """
    logging.debug(f"Unpacking {path}")
    runCommand(f'"{unpackAssets}" "{path}" "{path}-unpacked"')
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
    templatePath = join(templatesDir, f"{character['content']['identity']['name']}.template")
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
    if os.path.exists(temporaryPath): os.remove(temporaryPath)
    runCommand(f'"{dumpJson}" "{path}" "{temporaryPath}"')
    logging.info(f"Created temporary json file from .player at {temporaryPath}")
    j = loadJson(temporaryPath)
    os.remove(temporaryPath)
    return j


def saveCharacter(path: str, data: {}):
    """
    Save the given data to a .player file at path
    """
    with open(temporaryPath, "w") as f:
        json.dump(data, f, indent=4)
        logging.debug(f"Dumped {data} to the temporary path")
    runCommand(f'"{makeJson}" "{temporaryPath}" "{path}"')
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
    for template in os.listdir(templatesDir):
        templates.append((template.replace(".template", ""), join(templatesDir, template)))
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
        for name in next(os.walk(profilesDir))[1]:
            try:
                for character in os.listdir(join(profilesDir, name, "storage", "player")):
                    if character.endswith(".player"):
                        path = join(profilesDir, name, "storage", "player", character)
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
