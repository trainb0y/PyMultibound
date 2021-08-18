import os, sys, logging
import menu
from profile import Profile
from util import Style, Fore, Back, load_settings

# Version of PyMultibound
version = "0.1-ALPHA"

# Fore, Back, etc. allow us to use colored text through Colorama
# It is automatically replaced with placeholder "" by settingsloader if colored-text is false
# How to use:
#    print(f"{Fore.RED}RED TEXT{Style.RESET_ALL}")
#    would print RED TEXT in the color red. f-strings make this
#    so much easier!

# Options:
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

logging.info(f"Initializing PyMultibound - {version}")

settings = load_settings()

steamapps_dir = os.path.join(
    *settings["steamapps-directory"])  # see docs on os.path.join
workshop_dir = os.path.join(steamapps_dir, "workshop", "content", "211820")
starbound_dir = os.path.join(steamapps_dir, "common", "Starbound")

logging.debug(f"Steamapps directory: {steamapps_dir}")
logging.debug(f"Workshop directory: {workshop_dir}")

profiles = []

# Iterate through profiles and create them
profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "profiles")
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
    logging.debug("Created profile selection menu")
    print(profile_menu.display())
    while True:
        try:
            option = int(input(">> "))
            result = profile_menu.callback(option)
            if result:
                logging.debug(f"User selected {result.name}")
                return result
            else:
                print(f"{Fore.RED}Please enter a number corresponding to a profile!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")

        print()
        print(profile_menu.display())


def load_profile():
    global current_profile
    """Switch the currently loaded profile for a different one"""
    # Have the user select a profile and then load it in
    # profile = select_profile(profiles)
    logging.debug("Asking user for load confirmation")
    if "y" in input(
            f"{Fore.GREEN}Load profile {current_profile.name}? {Fore.YELLOW}This will erase the current game data!\n" +
            "(Save it as a profile/update the profile first) (Y/N) ").lower():
        current_profile.load()
        return True
    else:
        logging.info("Profile load aborted")
        return False


def switch_profile():
    """Switch current profile but do no file manipulation"""
    global current_profile
    current_profile.unload()
    current_profile = select_profile(profiles)


def new_profile():
    """Create a new profile"""
    profile_name = input("Enter profile name: ")
    profile = Profile()
    profile.create(profile_name, starbound_dir, workshop_dir)
    profiles.append(profile)


def edit_profile():
    """Edit profile menu (for changing name, etc)"""
    print(f"{Fore.MAGENTA}Profile editing menu coming soon!")


def delete_profile():
    """Deletes a profile"""
    # Have the user select a profile and then "delyeet" it
    profile = select_profile(profiles)
    logging.debug("Asking user for profile delete confirmation ")
    if "y" in input(f"{Fore.GREEN}Delete profile {profile.name}? {Fore.YELLOW}This IS NOT REVERSABLE! (Y/N) ").lower():
        profile.unload()
        profile.delete()
        profiles.remove(profile)
        print(f"{Fore.GREEN}Deleted {profile.name}")
        logging.info(f"Deleted profile {profile.name}")
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

This program works by taking snapshots, called "profiles" of the
important parts of the main starbound directory.

When you want to play a profile, it deletes the contents of the "mods"
and "storage" folders inside of the Starbound folder and replaces them 
with the contents of the selected profile.

{Fore.CYAN}
---- PyMultibound Menu Options ---- 
{Fore.GREEN}Help{Style.RESET_ALL}:           Brings up this message (clearly you know this by now)
{Fore.GREEN}Run Starbound{Style.RESET_ALL}:  This will run Starbound, with the currently installed profile
        This works by deleting the current Starbound "mods" and "storage" folders,
        and replacing them with the saved ones for this profile.
        
        The current profile will be auto-updated when you quit starbound.
{Fore.GREEN}Update Profile{Style.RESET_ALL}: This sets the profile"s data to whatever is currently in the Starbound folder
        {Fore.YELLOW}WARNING: if used while Starbound folder is empty, this can
        effectively delete the current profile!
{Fore.GREEN}Switch Profile{Style.RESET_ALL}: Change the currently selected profile
{Fore.GREEN}New Profile{Style.RESET_ALL}:    Creates a new profile, but does not define any mods/universe
        Use "Update Profile" with the new profile selected to define mods
{Fore.GREEN}Edit Profile{Style.RESET_ALL}:   {Fore.RED}{Back.YELLOW}WIP{Style.RESET_ALL} This will eventually let you edit profile details.
        For now, profiles must be edited manually. 
            - You can change the profile name by changing the name of its folder
                inside of the "profiles" folder
            - You can add or remove mods directly from the "mods" folder inside of
                the profile"s folder
            - You can access the universe/save stuff in the "storage" folder inside
                of the profile"s folder
{Fore.GREEN}Delete Profile{Style.RESET_ALL}:  This will completely delete all of the selected profile"s data.
{Fore.GREEN}Quit{Style.RESET_ALL}: Quit the program
    

    """)


def run_starbound():
    """Run starbound as it is now, and update the current profile on exit"""
    global current_profile
    if not load_profile():  # it failed
        return
    logging.info("Starting starbound...")
    cmd = os.path.join(starbound_dir, "win64", "starbound.exe")
    # os.path.join() does not escape spaces, so
    # it thinks you are trying to run
    # C:/Program because of the space in program files
    # So, have to do some string work lol
    os.system(f'"{cmd}"')  # Run the game
    logging.info("Starbound closed, updating profile")
    print(f"{Fore.GREEN}Updating profile, please wait...")
    print(f"{Fore.YELLOW}This may take a while if you have a large universe or many mods")
    current_profile.unload()
    print(f"{Fore.GREEN}Profile {current_profile.name} updated!")
    if settings["compress-profiles"]:
        print(f"{Fore.GREEN}Compressing {current_profile.name}. This may take a while.")
        print(f"{Fore.GREEN}Profile compression can be disabled in settings.json!")
        current_profile.compress()
        print(f"{Fore.GREEN}Profile compressed!")


def quit_program():
    global current_profile
    current_profile.unload()
    print(f"{Fore.CYAN}Profiles saved, quitting...")
    logging.info(f"Quitting PyMultibound - {version}")
    sys.exit()


if __name__ == "__main__":

    print(f"{Fore.CYAN}PyMultibound - {version}")
    print(f"{Fore.GREEN}By trainb0y1")
    print()

    if settings["backup-warning"]:
        logging.debug("settings['backup-warning'] is True")
        print(
            f"{Fore.RED}{Back.YELLOW}{Style.BRIGHT}BE SURE TO MAKE A BACKUP BEFORE USING, THIS WILL DELETE THE STARBOUND DATA (See help for more info){Style.RESET_ALL}")
        print(f"{Fore.RED} To disable this message, set backup-warning to false in settings.json")
    logging.debug("Entering main menu loop")
    while True:  # Main Menu Loop
        main_menu = menu.Menu(
            "Main Menu", [
                ("Help", help_page),
                (f"Run Starbound ({Fore.CYAN + current_profile.name + Style.RESET_ALL})", run_starbound),
                ("Switch Profile", switch_profile),
                (f"Update Profile ({Fore.CYAN + current_profile.name + Style.RESET_ALL})", current_profile.update),
                ("New Profile", new_profile),
                ("Edit Profile", edit_profile),
                ("Delete Profile", delete_profile),
                ("Quit", quit_program)])
        # I put the menu definition in here so that the profile names can update
        # With this outside, even when you switch profiles it will say you are on 
        # the first one
        print()
        print(main_menu.display())

        try:
            option = int(input(">> "))
            result = main_menu.callback(option)
            if result:
                result()
            else:
                print(f"{Fore.RED}Please enter a number corresponding to an option!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")
