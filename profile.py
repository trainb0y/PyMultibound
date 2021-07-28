import os, shutil

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

class Profile():

    def create(self,name, starbound_dir, workshop_dir):
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")

        # Now we make a directory for this particular profile, inside of the saves dir
        profile_dir = os.path.join(profiles_dir,name)
        
        for directory in [os.path.join(profile_dir,"mods"),os.path.join(profile_dir,"storage")]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.name = name # Save the name
        self.directory = profile_dir
        self.starbound_dir = starbound_dir
        self.workshop_dir = workshop_dir
        self.loaded = False
        

    def clear_starbound(self):
        """Delete all of the profile specific stuff in the starbound and workshop folders"""
        if self.loaded:
            print(f"{Fore.YELLOW}Clearing Starbound directory while profile {self.name} is loaded! Are you sure you want to procede? (Y/N)")
            if "y" not in input(f"{Fore.RED}THIS WILL CLEAR THIS PROFILE").lower():
                return
        for directory in ["mods","storage"]:
            for d in [os.path.join(self.starbound_dir,directory)]:
                if os.path.exists(d): shutil.rmtree(d)



    def load(self):
        """Load this profile into the starbound install"""
        self.clear_starbound()
        for directory in ["mods","storage"]:
            shutil.move(os.path.join(self.directory,directory),self.starbound_dir)
        self.loaded = True
        
    def unload(self):
        """Bascially update(), but sets loaded to False and clears the Starbound dir"""
        print(f"{Fore.GREEN}Unloading {self.name}...")
        self.update()
        self.clear_starbound()
        self.loaded = False
        print(f"{Fore.GREEN}Unloaded {self.name}")
        

    def update(self):
        """Update this profile with the current starbound data"""
        if not self.loaded:
            if "y" not in input(f"{Fore.YELLOW}Profile {self.name} is not currently loaded.\nAre you sure you want to update it? (Y/N)").lower(): return

        
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

        print(f"{Fore.GREEN}Updating {self.name}...")
        # This next chunk bothers me.
        # I feel like I should be able to get it done with one try/except and
        # iterate through the types, but right now I lack the brainpower
        # TODO: Clean this up!
        try: # Mods
            shutil.move(os.path.join(self.starbound_dir,"mods"),os.path.join(self.directory,"mods"))
        except FileNotFoundError: 
            print(f"{Fore.RED}Failed to update mods: Mods folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory,"mods")):
                os.makedirs(os.path.join(self.directory,"mods"))

        try: # Storage
            shutil.move(os.path.join(self.starbound_dir,"storage"),os.path.join(self.directory,"storage"))
        except FileNotFoundError: 
            print(f"{Fore.RED}Failed to update storage: Storage folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory,"storage")):
                os.makedirs(os.path.join(self.directory,"storage"))

        # Now for the hard part, workshop mods
        # Workshop mods are stored inside of the workshop_dir in folders with numerical names
        # Inside of those folders are files named contents.pak
        # First, we want to ask if we should include these workshop mods in the profile
        # If so, we should move the .pak s to our mods folder, and rename them
        # to workshop-mod-(numerical id)

        if len(next(os.walk(self.workshop_dir))[1]) > 0:
            if "y" not in input(f"{Fore.YELLOW}Steam Workshop mods detected, would you like to add them to the profile?{Style.RESET_ALL} (Y/N) ").lower():
                print(f"{Fore.GREEN}Steam workshop mods ignored")
                print(f"{Fore.GREEN}Updated {self.name}")
                return

            for name in next(os.walk(self.workshop_dir))[1]:
                # Basically for numerically id-ed folder
                if not os.path.isfile(os.path.join(self.workshop_dir,name,"contents.pak")):
                    print(f"{Fore.YELLOW}No contents.pak found in workshop mod {name}")
                else:
                    shutil.move(
                        os.path.join(self.workshop_dir,name,"contents.pak"),
                        os.path.join(self.directory,"mods",f"workshop-mod-{name}.pak")
                    )
                    print(f"Installed workshop mod {name}")
                     
            print(f"{Fore.GREEN}Workshop mods added to profile, please unsubscribe from them")
            print(f"{Fore.GREEN}Updated {self.name}")
        
    

    def delete(self):
        """Delete all files relating to this profile"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")
        shutil.rmtree(os.path.join(profiles_dir,self.name))
        self.loaded = False

    

    
    


    

    
