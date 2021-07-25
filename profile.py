import os, shutil

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
        

    def clear_starbound(self):
        """Delete all of the profile specific stuff in the starbound and workshop folders"""
        for directory in ["mods","storage"]:
            for d in [os.path.join(self.starbound_dir,directory)]:
                if os.path.exists(d): shutil.rmtree(d)



    def load(self):
        """Load this profile into the starbound install"""
        self.clear_starbound()
        for directory in ["mods","storage"]:
            shutil.move(os.path.join(self.directory,directory),self.starbound_dir)
        
        

    def update(self):
        """Update this profile with the current starbound data"""
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)


        # This next chunk bothers me.
        # I feel like I should be able to get it done with one try/except and
        # iterate through the types, but right now I lack the brainpower
        # TODO: Clean this up!
        try: # Mods
            shutil.move(os.path.join(self.starbound_dir,"mods"),os.path.join(self.directory,"mods"))
        except FileNotFoundError: 
            print("Failed to update mods: Mods folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory,"mods")):
                os.makedirs(os.path.join(self.directory,"mods"))

        try: # Storage
            shutil.move(os.path.join(self.starbound_dir,"storage"),os.path.join(self.directory,"storage"))
        except FileNotFoundError: 
            print("Failed to update storage: Storage folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory,"storage")):
                os.makedirs(os.path.join(self.directory,"storage"))

        # Now for the hard part, workshop mods
        # Workshop mods are stored inside of the workshop_dir in folders with numerical names
        # Inside of those folders are files named contents.pak
        # First, we want to ask if we should include these workshop mods in the profile
        # If so, we should move the .pak s to our mods folder, and rename them
        # to workshop-mod-(numerical id)

        if len(next(os.walk(self.workshop_dir))[1]) > 0:
            if "y" not in input("Steam Workshop mods detected, would you like to add them to the profile? (Y/N) "):
                print("Steam workshop mods ignored")
                return

            for name in next(os.walk(self.workshop_dir))[1]:
                # Basically for numerically id-ed folder
                if not os.path.isfile(os.path.join(self.workshop_dir,name,"contents.pak")):
                    print(f"No contents.pak found in workshop mod {name}")
                    return
                shutil.move(
                    os.path.join(self.workshop_dir,name,"contents.pak"),
                    os.path.join(self.directory,"mods",f"workshop-mod-{name}.pak")
                )
                print(f"Installed workshop mod {name}")
                     
            print("Workshop mods added to profile, please unsubscribe from them")
    

    def delete(self):
        """Delete all files relating to this profile"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")
        shutil.rmtree(os.path.join(profiles_dir,self.name))

    

    
    


    

    
