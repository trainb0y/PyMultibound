import logging, os, json
import menu
from os.path import join
from util import Style, Fore, Back, load_settings


# Starbound character appearance editor
# Allows people to create appearance "templates" from existing characters
# and then lets them apply the templates to existing characters, overwriting
# the existing appearance data in the .player file

class ExitedException(Exception): pass


settings = load_settings()

profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "profiles")
steamapps_dir = os.path.join(
    *settings["steamapps-directory"])  # see docs on os.path.join
starbound_dir = os.path.join(steamapps_dir, "common", "Starbound")
# Yes, I know I'm defining all of these twice, but whatever
# TODO: Move these to util.py?

temp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
templates_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

dump_json = join(starbound_dir, "win32", "dump_versioned_json.exe")  # path to the dump_versioned_json.exe
make_json = join(starbound_dir, "win32", "make_versioned_json.exe")  # path to the make_versioned_json.exe


def character_editor_menu():
    logging.info("Switched to profile editor loop")
    print(f"{Fore.RED}THIS IS EXPERIMENTAL, PLEASE MAKE A BACKUP OF YOUR CHARACTER BEFORE CONTINUING")
    try:
        while True:
            editor_menu = menu.Menu(
                "Character Editor", [
                    ("Find Players", select_player),
                    ("Make Template", make_template),
                    ("Apply Template", apply_template),
                    ("Delete Template", delete_template),
                    ("Exit to Main Menu", exit_editor)])

            print(editor_menu.display())

            try:
                option = int(input(">> "))
                result = editor_menu.callback(option)
                if result:
                    result()
                else:
                    print(f"{Fore.RED}Please enter a number corresponding to an option!")
            except ValueError as e:
                print(f"{Fore.RED}Please enter a number! {e}")

    except ExitedException:
        logging.info("Exited editor loop")


def exit_editor():
    logging.info("Exiting editor loop")
    raise ExitedException


def make_template(): pass


def apply_template(): pass


def delete_template(): pass


def select_player():
    character_filenames = []
    try:
        for name in next(os.walk(profiles_dir))[1]:
            for character in os.listdir(join(profiles_dir, name, "storage", "player")):
                if character.endswith(".player"):
                    character_filenames.append(join(profiles_dir, name, "storage", "player", character))
    except StopIteration:
        logging.info("No existing profiles found!")

    # For each filename, get the character's actual name
    characters = []
    for filename in character_filenames:
        command = f'"{dump_json}" "{filename}" "{join(temp_dir, "tempchar.json")}"'
        os.system(f'"{command}"')
        with open(join(temp_dir, "tempchar.json"), "r") as f:
            raw = f.read()
            raw = raw.replace("inf,", "999999999,")  # FU uses "inf" which is invalid, so replace it with a big number
            # It should automatically overwrite this anyway.
            player_json = json.loads(raw)
            characters.append((f'{player_json["content"]["identity"]["name"]} - {player_json["content"]["uuid"]}',filename))

    character_menu = menu.Menu(
        "Select a Character", characters)

    print(character_menu.display())
    while True:
        try:
            option = int(input(">> "))
            result = character_menu.callback(option)
            if result:
                return result
            else:
                print(f"{Fore.RED}Please enter a number corresponding to a character!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")

        print()
        print(character_menu.display())

