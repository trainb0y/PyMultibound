
import os
import menu
from profile import Profile
from colorama import Style, Fore, Back, init
        # Allows us to use colored text
        # How to use:
        #    print(f"{Fore.RED}RED TEXT{Style.RESET_ALL}")
        #    would print RED TEXT in the color red. f-strings make this
        #    so much easier!

        # Options:
        # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
        # Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
        # Style: DIM, NORMAL, BRIGHT, RESET_ALL

init(autoreset=True) # Should make this work for more windows use cases
                     # also will remove the need to reset color after each line.

steamapps_dir = os.path.join(os.path.expanduser("~"),"/Program Files (x86)/Steam/steamapps")
profiles = [Profile(),Profile()]
profiles[0].name = "test1"
profiles[1].name = "test2"

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
            if result: return result
            else: print(f"{Fore.RED}Please enter a number corresponding to a profile!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")

        print()
        print(profile_menu.display())



def load_profile():
    # Have the user select a profile and then load it in
    profile = select_profile(profiles)
    if "y" in input(f"{Fore.GREEN}Load profile {profile.name}? {Fore.YELLOW}This will erase the current game data!\n"+
        "(Save it as a profile/update the profile first) (Y/N) ").lower():
        profile.load(steamapps_dir)
    else: print(f"\n{Fore.YELLOW}Profile load aborted")
    

def new_profile():
    name = input("Enter profile name: ")
    profile = Profile()
    profile.create(name, steamapps_dir)
    
def update_profile():
    profile = select_profile(profiles)
    profile.update()
   
    

def edit_profile(): pass


def delete_profile():
    # Have the user select a profile and then "delyeet" it
    profile = select_profile(profiles)
    if "y" in input(f"{Fore.GREEN}Delete profile {profile.name}? {Fore.YELLOW}This IS NOT REVERSABLE! (Y/N) ").lower():
        profile.delete(steamapps_dir)
    else: print(f"\n{Fore.YELLOW}Profile deletion aborted")


def help_page():
    print(
"""
Yeah... help text comes later
"""
    )


if __name__ == "__main__":

    print(f"{Fore.CYAN}PyMultibound - v0.1")
    print(f"{Fore.GREEN}By trainb0y1")

    main_menu = menu.Menu(
        "Main Menu - Please Select an Option", [
        ("Help",help_page),
        ("Load Profile", load_profile),
        ("Update Profile", update_profile),
        ("New Profile", new_profile),
        ("Edit Profile", edit_profile),
        ("Delete Profile", delete_profile)])

    print(main_menu.display())
    while True: # Main Menu Loop
        try:
            option = int(input('>> '))
            result = main_menu.callback(option)
            if result != False: result()
            else: print(f"{Fore.RED}Please enter a number corresponding to an option!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")

        print()
        print(main_menu.display())
