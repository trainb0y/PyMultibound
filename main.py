
import os, sys
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

steamapps_dir = os.path.join("c:\\","Program Files (x86)","Steam","steamapps") # see docs on os.path.join 
workshop_dir = os.path.join(steamapps_dir, "workshop","content","211820")
starbound_dir = os.path.join(steamapps_dir,"common","Starbound")
print(starbound_dir)

profiles = []

# Iterate through profiles and create them
profiles_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"profiles")
for name in next(os.walk(profiles_dir))[1]:
    prof = Profile()
    prof.create(name,starbound_dir,workshop_dir)
    profiles.append(prof)

# If we don't have a vanilla profile, make one
vanilla_exists = False
for prof in profiles:
    if prof.name == "Vanilla":
        vanilla_exists = True

if not vanilla_exists:
    vanilla = Profile()
    vanilla.create("Vanilla",starbound_dir,workshop_dir)

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
            if result: return result
            else: print(f"{Fore.RED}Please enter a number corresponding to a profile!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")

        print()
        print(profile_menu.display())



def load_profile():
    global current_profile
    """Switch the currently loaded profile for a different one"""
    # Have the user select a profile and then load it in
    # profile = select_profile(profiles)
    if "y" in input(f"{Fore.GREEN}Load profile {current_profile.name}? {Fore.YELLOW}This will erase the current game data!\n"+
        "(Save it as a profile/update the profile first) (Y/N) ").lower():
        current_profile.load()
    else: print(f"\n{Fore.YELLOW}Profile load aborted")


def switch_profile():
    """Switch current profile but do no file manipulation"""
    global current_profile
    current_profile = select_profile(profiles)

    

def new_profile():
    """Create a new profile"""
    name = input("Enter profile name: ")
    profile = Profile()
    profile.create(name, starbound_dir, workshop_dir)
    profiles.append(profile)
    
def edit_profile(): 
    """Edit profile menu (for changing name, etc)"""
    print(f"{Fore.MAGENTA}Profile editing menu coming soon!")


def delete_profile():
    """Deletes a profile"""
    # Have the user select a profile and then "delyeet" it
    profile = select_profile(profiles)
    if "y" in input(f"{Fore.GREEN}Delete profile {profile.name}? {Fore.YELLOW}This IS NOT REVERSABLE! (Y/N) ").lower():
        profile.delete(steamapps_dir)
        profiles.remove(profile)
    else: print(f"\n{Fore.YELLOW}Profile deletion aborted")



def help_page():
    """Show a basic description of the options"""
    print(f"{Fore.MAGENTA}Yeah... help text comes later")

def run_starbound():
    """Run starbound as it is now, and update the current profile on exit"""
    global current_profile
    load_profile()
    cmd = os.path.join(starbound_dir,"win64","starbound.exe")
    # os.path.join() does not escape spaces, so
    # it thinks you are trying to run
    # C:/Program beacause of the space in program files
    # So, have to do some string work lol
    os.system(f'"{cmd}"')  # Run the game
    print(f"{Fore.GREEN}Updating profile, please wait...")
    print(f"{Fore.YELLOW}This may take a while if you have a large universe or many mods")
    current_profile.update()
    print(f"{Fore.GREEN}Profile {current_profile.name} updated!")


if __name__ == "__main__":

    print(f"{Fore.CYAN}PyMultibound - v0.1")
    print(f"{Fore.GREEN}By trainb0y1")
    while True: # Main Menu Loop
        main_menu = menu.Menu(
        "Main Menu - Please Select an Option", [
        ("Help",help_page),
        (f"Run Starbound ({current_profile.name})",run_starbound),
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
            if result != False: result()
            else: print(f"{Fore.RED}Please enter a number corresponding to an option!")
        except ValueError:
            print(f"{Fore.RED}Please enter a number!")
