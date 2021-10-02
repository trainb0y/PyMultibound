import menu
from util import *


# Starbound character appearance editor
# Allows people to create appearance "templates" from existing characters
# and then lets them apply the templates to existing characters, overwriting
# the existing appearance data in the .player file

# TODO: make it work with compressed profiles
# TODO: Better error handling with missing player folder/file
# TODO: Logging
# TODO: Comment a lot

class ExitedException(Exception): pass


def character_editor_menu():
    logging.info("Switched to profile editor loop")
    print(f"{Fore.RED}THIS IS EXPERIMENTAL, PLEASE MAKE A BACKUP OF YOUR CHARACTER BEFORE CONTINUING")
    editor_menu = menu.Menu(
        "Character Editor", [
            ("Make Template", make_template),
            ("Apply Template", apply_template),
            ("Delete Template", delete_template),
            ("Exit to Main Menu", exit_editor)
        ]
    )
    try:
        while True:
            editor_menu.select()()

    except ExitedException:
        logging.info("Exited editor loop")


def load_character_json(path):
    with open(path, "r") as f:
        raw = f.read()
        raw = raw.replace("inf,", "999999999,")  # FU uses "inf" which is invalid, so replace it with a big number
        # It should automatically overwrite this anyway.
        logging.info("Returning python object")
        return json.loads(raw)


def load_character_file(path):
    logging.info(f"Loading python object from {path}")
    if os.path.exists(join(temp_dir, "tempchar.json")):
        os.remove(join(temp_dir, "tempchar.json"))
    command = f'"{dump_json}" "{path}" "{join(temp_dir, "tempchar.json")}"'
    os.system(f'"{command}"')
    logging.info("Created temporary json file from .player")
    return load_character_json(join(temp_dir, "tempchar.json"))


def create_character_file(directory, contents):
    logging.info("Attempting to recreate .player file")
    with open(join(temp_dir, "tempchar.json"), "w") as f:
        json.dump(contents, f, indent=4)

    command = f'"{make_json}" "{join(temp_dir, "tempchar.json")}" "{join(directory, str(contents["content"]["uuid"]) + ".player")}"'
    print(f'Destination: {join(directory, str(contents["content"]["uuid"]) + ".player")}')
    os.system(f'"{command}"')


def exit_editor():
    logging.info("Exiting editor loop")
    raise ExitedException


def make_template():
    logging.info("Attempting to create a new template")
    template_character = load_character_file(select_character())
    name = input("Template name: ")
    with open(join(templates_dir, f"{name}.template"), "w+") as f:
        json.dump(template_character["content"]["identity"], f, indent=4)
    logging.info(f"Saved template {name}")


def apply_template():
    original_file = select_character()
    original_character = load_character_file(original_file)
    with open(select_template(), "r") as f:
        template = json.load(f)
    if "y" in input("Preserve character name? (y/n) ").lower():
        template["name"] = original_character["content"]["identity"]["name"]

    original_character["content"]["identity"] = template
    if "y" in input("Are you sure you want to do this? (y/n) ").lower():
        create_character_file(os.path.dirname(original_file), original_character)
    else:
        print("Aborted")


def delete_template():
    logging.info("Attempting to delete a template")
    template = select_template()
    if "y" in input(f"{Fore.YELLOW}Are you sure you want to delete this template? (y/n) ").lower():
        os.remove(template)
        print(f"{Fore.GREEN}Deleted template.")
    logging.info("Deleted template")


def select_template():
    templates = []
    for template in os.listdir(templates_dir):
        templates.append((template.replace(".template", ""), join(templates_dir, template)))

    template_select_menu = menu.Menu(
        "Select a Template", templates)

    return template_select_menu.select()


def select_character():
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
        player_json = load_character_file(filename)
        characters.append(
            (f'{player_json["content"]["identity"]["name"]} - {player_json["content"]["uuid"]}', filename))

    character_menu = menu.Menu(
        "Select a Character", characters)
    return character_menu.select()
