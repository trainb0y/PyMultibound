import os, sys, json
import menu
from profile import Profile
from colorama import Style, Fore, Back, init

# Colorama allows us to use colored text
# How to use:
#    print(f"{Fore.RED}RED TEXT{Style.RESET_ALL}")
#    would print RED TEXT in the color red. f-strings make this
#    so much easier!

# Options:
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

init(autoreset=True)  # Should make this work for more windows use cases
# also will remove the need to reset color after each line.


# If the settings.json file does not exist, create it
if not os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json"), "x") as f:
        json.dump({
            "backup-warning": True,
            "colored-text": True,
            "steamapps-directory": ("c:\\", "Program Files (x86)", "Steam", "steamapps")
        }, f)


class PlaceHolder:  # There has GOT to be a better way to do this
    """
        A placeholder class to replace colorama codes with.
        The entire idea of having to make this just rubs me the wrong
        way. 
        """

    def __init__(self):
        self.BLACK, self.RED, self.GREEN, self.YELLOW = '', '', '', ''
        self.BLUE, self.MAGENTA, self.CYAN, self.WHITE, self.RESET = '', '', '', '', ''
        self.DIM, self.NORMAL, self.BRIGHT, self.RESET_ALL = '', '', '', ''


with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")) as f:
    settings = json.load(f)

if not settings["colored-text"]:  # Disable colorama
    Style, Fore, Back = PlaceHolder(), PlaceHolder(), PlaceHolder()

steamapps_dir = os.path.join(
    *settings["steamapps-directory"])  # see docs on os.path.join
workshop_dir = os.path.join(steamapps_dir, "workshop", "content", "211820")
starbound_dir = os.path.join(steamapps_dir, "common", "Starbound")

profiles = []

# Iterate through profiles and create them
profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "profiles")
try:
    for name in next(os.walk(profiles_dir))[1]:
        prof = Profile()
        prof.create(name, starbound_dir, workshop_dir)
        profiles.append(prof)
except StopIteration:
    pass  # no profiles

# If we don't have a vanilla profile, make one
vanilla_exists = False
for prof in profiles:
    if prof.name == "Vanilla":
        vanilla_exists = True

if not vanilla_exists:
    vanilla = Profile()
    vanilla.create("Vanilla", starbound_dir, workshop_dir)
    profiles.append(vanilla)

current_profile = profiles[0]


def select_profile(profiles):
    """Menu screen, returns a profile from the list of profiles provided"""
    profile_options = []
    for profile in profiles:
        profile_options.append((profile.name, profile))

    profile_menu = menu.Menu(
        "Select a Profile", profile_options)

    print(profile_menu.display())
    while True:
        try:
            option = int(input('>> '))
            result = profile_menu.callback(option)
            if result:
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
    if "y" in input(
            f"{Fore.GREEN}Load profile {current_profile.name}? {Fore.YELLOW}This will erase the current game data!\n" +
            "(Save it as a profile/update the profile first) (Y/N) ").lower():
        current_profile.load()
        return True
    else:
        print(f"\n{Fore.YELLOW}Profile load aborted")
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
    if "y" in input(f"{Fore.GREEN}Delete profile {profile.name}? {Fore.YELLOW}This IS NOT REVERSABLE! (Y/N) ").lower():
        profile.unload()
        profile.delete()
        profiles.remove(profile)
    else:
        print(f"\n{Fore.YELLOW}Profile deletion aborted")


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
{Fore.GREEN}Update Profile{Style.RESET_ALL}: This sets the profile's data to whatever is currently in the Starbound folder
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
                the profile's folder
            - You can access the universe/save stuff in the "storage" folder inside
                of the profile's folder
{Fore.GREEN}Delete Profile{Style.RESET_ALL}:  This will completely delete all of the selected profile's data.
{Fore.GREEN}Quit{Style.RESET_ALL}: Quit the program
    

    """)


def run_starbound():
    """Run starbound as it is now, and update the current profile on exit"""
    global current_profile
    if not load_profile():  # it failed
        return
    cmd = os.path.join(starbound_dir, "win64", "starbound.exe")
    # os.path.join() does not escape spaces, so
    # it thinks you are trying to run
    # C:/Program beacause of the space in program files
    # So, have to do some string work lol
    os.system(f'"{cmd}"')  # Run the game
    print(f"{Fore.GREEN}Updating profile, please wait...")
    print(f"{Fore.YELLOW}This may take a while if you have a large universe or many mods")
    print(f"{Fore.GREEN}Profile {current_profile.name} updated!")


if __name__ == "__main__":

    print(f"{Fore.CYAN}PyMultibound - v0.1")
    print(f"{Fore.GREEN}By trainb0y1")
    print()

    if settings["backup-warning"]:
        print(
            f'{Fore.RED}{Back.YELLOW}{Style.BRIGHT}BE SURE TO MAKE A BACKUP BEFORE USING, THIS WILL DELETE THE STARBOUND DATA (See help for more info){Style.RESET_ALL}')
        print(f'{Fore.RED} To disable this message, set backup-warning to false in settings.json')
    while True:  # Main Menu Loop
        main_menu = menu.Menu(
            "Main Menu - Please Select an Option", [
                ("Help", help_page),
                (f"Run Starbound ({current_profile.name})", run_starbound),
                ("Switch Profile", switch_profile),
                (f"Update Profile ({current_profile.name})", current_profile.update),
                ("New Profile", new_profile),
                ("Edit Profile", edit_profile),
                ("Delete Profile", delete_profile),
                ("Quit", sys.exit)])
        # I put the menu definition in here so that the profile names can update
        # With this outside, even when you switch profiles it will say you are on 
        # the first one
        print()
        print(main_menu.display())

        try:
            option = int(input('>> '))
            result = main_menu.callback(option)
            if result:
                result()
            else:
                print(f'{Fore.RED}Please enter a number corresponding to an option!')
        except ValueError:
            print(f'{Fore.RED}Please enter a number!')
