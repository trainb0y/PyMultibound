import os, shutil

class Profile():

    def create(self,name, steamapps_dir):
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")
        # Find the saves directory, if it doesn't exist, make it
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        # Now we make a directory for this particular profile, inside of the saves dir
        profile_dir = os.path.join(profiles_dir,name)
        os.mkdir(profile_dir)

        self.name = name # Save the name
        self.directory = profile_dir
        self.steamapps_dir = steamapps_dir


    def load(self):
        """Load this profile into the starbound install"""

    def update(self):
        """Update this profile with the current starbound data"""

    def delete(self):
        """Delete all files relating to this profile"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir,"profiles")
        shutil.rmtree(os.path.join(profiles_dir,self.name))

    

    
    


    

    
