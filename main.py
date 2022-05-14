import sys

import editor
from PyMultibound import menu
import util
from profile import Profile
from util import *

# Version of PyMultibound
version = "0.3-ALPHA"

# Fore, Back, etc. allow us to use colored text through Colorama
# It is automatically replaced with placeholder "" by util.py if colored-text is false
# How to use:
#    print(f"{Fore.RED}RED TEXT{Style.RESET_ALL}")
#    would print RED TEXT in the color red. f-strings make this
#    so much easier!

# Options:
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

logging.info(f"Initializing PyMultibound - {version}")

logging.info(f"Settings: {settings}")

logging.debug(f"Steamapps directory: {steamapps_dir}")
logging.debug(f"Workshop directory: {workshop_dir}")

profiles = []

# Iterate through profiles and create them
profiles_dir = join(os.path.dirname(os.path.realpath(__file__)), "profiles")
try:
    for name in next(os.walk(profiles_dir))[1]:
        prof = Profile()
        prof.create(name, starbound_dir, workshop_dir)
        profiles.append(prof)
except StopIteration:
    logging.info("No existing profiles found!")
    pass  # no profiles

# If we don"t have a vanilla profile, make one
vanilla_exists = False
for prof in profiles:
    if prof.name == "Vanilla":
        vanilla_exists = True
        logging.debug("Found Vanilla profile")

if not vanilla_exists:
    logging.info("Creating Vanilla profile")
    vanilla = Profile()
    vanilla.create("Vanilla", starbound_dir, workshop_dir)
    profiles.append(vanilla)

current_profile = profiles[0]
logging.debug(f"Set current profile to {current_profile}")


def select_profile(profiles):
    """Menu screen, returns a profile from the list of profiles provided"""
    logging.debug(f"Creating profile selection menu")
    profile_options = []
    for profile in profiles:
        profile_options.append((profile.name, profile))

    profile_menu = menu.Menu(
        "Select a Profile", profile_options)
    return profile_menu.select()


def switch_profile():
    """Switch current profile"""
    global current_profile
    current_profile = select_profile(profiles)


def new_profile():
    """Create a new profile"""
    profile_name = input("Enter profile name: ")
    if profile_name.strip() == "":
        print(f"{Fore.YELLOW}Profile name must not be empty!")
        return  # 0 character names have all sorts of issues, and deleting them
        # deletes all profiles, as I painfully learned from experience

    profile = Profile()
    profile.create(profile_name, starbound_dir, workshop_dir)
    profiles.append(profile)
    if "y" in input("Move current Starbound data into profile? ").lower():
        profile.get_starbound_data(starbound_dir, workshop_dir)


def delete_profile():
    global current_profile
    """Deletes a profile"""
    # Have the user select a profile and then "delyeet" it
    profile = select_profile(profiles)
    logging.debug("Asking user for profile delete confirmation ")
    if "y" in input(f"{Fore.GREEN}Delete profile {profile.name}? {Fore.YELLOW}This IS NOT REVERSABLE! (Y/N) ").lower():
        profile.delete()
        profiles.remove(profile)
        print(f"{Fore.GREEN}Deleted {profile.name}")
        logging.info(f"Deleted profile {profile.name}")
        current_profile = select_profile(profiles)
    else:
        print(f"\n{Fore.YELLOW}Profile deletion aborted")
        logging.info(f"Aborted deletion of {profile.name}")


def help_page():
    """Show a basic description of the options"""
    print(f"""{Fore.CYAN}
-------------------- PyMultibound Help --------------------
{Style.RESET_ALL}
Most of the options should be self-explanatory, but some aspects
of this mod manager need a bit of explanation.

{Fore.CYAN}
---- PyMultibound Menu Options ---- 
{Fore.GREEN}Help{Style.RESET_ALL}:            Brings up this message (clearly you know this by now)
{Fore.GREEN}Run Starbound{Style.RESET_ALL}:   Run Starbound with the currently selected profile
{Fore.GREEN}Switch Profile{Style.RESET_ALL}:  Change the currently selected profile
{Fore.GREEN}New Profile{Style.RESET_ALL}:     Creates a new profile, optionally moving the current Starbound save into this profile
{Fore.GREEN}Delete Profile{Style.RESET_ALL}:  This will completely delete all of the selected profile"s data.
{Fore.GREEN}Quit{Style.RESET_ALL}: Quit the program
    
    """)


def run_starbound():
    """Run starbound as it is now, and update the current profile on exit"""
    global current_profile
    if not current_profile.load():  # it failed
        logging.error(f"Failed to load profile {current_profile.name}, not starting Starbound.")
        return
    logging.info("Starting starbound...")
    cmd = f'"{util.starbound_executable}" ' \
          f'-bootconfig "{join(current_profile.directory, "sbinit.config")}"'
    logging.info(f"Launch command: {cmd}")

    if platform.system() == "Windows": os.system(f'"{cmd}"')  # Run the game
    if platform.system() == "Linux": os.system(cmd)  # TODO: find out why windows needs the extra "s
    # Windows crashes without the "s, and linux crashes with them.

    if settings["compress-profiles"]:
        print(f"{Fore.GREEN}Compressing {current_profile.name}. This may take a while.")
        print(f"{Fore.GREEN}Profile compression can be disabled in settings.json!")
        current_profile.compress()
        print(f"{Fore.GREEN}Profile compressed!")


def quit_program():
    shutil.rmtree(temp_dir)
    print(f"{Fore.CYAN}Profiles saved, quitting...")
    logging.info(f"Quitting PyMultibound - {version}")
    sys.exit()


if __name__ == "__main__":

    print(f"{Fore.CYAN}PyMultibound - {version}")
    print(f"{Fore.GREEN}By trainb0y1")
    print()

    logging.debug("Entering main menu loop")
    while True:  # Main Menu Loop
        main_menu = menu.Menu(
            "Main Menu", [
                ("Help", help_page),
                (f"Run Starbound ({Fore.CYAN + current_profile.name + Style.RESET_ALL})", run_starbound),
                ("Switch Profile", switch_profile),
                ("New Profile", new_profile),
                ("Delete Profile", delete_profile),
                ("Character Appearance Editor", editor.character_editor_menu),
                ("Quit", quit_program)])

        main_menu.select()()
