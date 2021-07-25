import os, shutil

class Profile():

    def create(self,name, starbound_dir):
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
        

    def clear_starbound(self):
        """Delete all of the profile specific stuff in the starbound folder"""
        for directory in ["mods","storage"]:
            if os.path.exists(os.path.join(self.starbound_dir,directory)):
                shutil.rmtree(os.path.join(self.starbound_dir,directory))
            #os.makedirs(os.path.join(self.starbound_dir,directory))



    def load(self):
        """Load this profile into the starbound install"""
        self.clear_starbound()
        for directory in ["mods","storage"]:
            shutil.move(os.path.join(self.directory,directory),self.starbound_dir)


    def update(self):
        """Update this profile with the current starbound data"""
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        shutil.move(os.path.join(self.starbound_dir,"mods"),os.path.join(self.directory,"mods"))
        shutil.move(os.path.join(self.starbound_dir,"storage"),os.path.join(self.directory,"storage"))

    def delete(self):
        """Delete all files relating to this profile"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")
        shutil.rmtree(os.path.join(profiles_dir,self.name))

    

    
    


    

    
