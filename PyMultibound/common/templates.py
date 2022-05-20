import json
import logging
import os
from os.path import join

from PyMultibound.common.paths import paths
from PyMultibound.common.util import loadJson, runCommand


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
