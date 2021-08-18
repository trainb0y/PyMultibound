import os, shutil, logging

import util
from util import Style, Fore, Back, load_settings

settings = util.load_settings()  # I know this means it gets called multiple
# times per run, but its a small little file operation and shouldn"t really matter


class Profile:

    def create(self, name, starbound_dir, workshop_dir):
        logging.info(f"Creating profile with name {name}, sb dir {starbound_dir} and workshop dir {workshop_dir}")
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir, "profiles")

        # Now we make a directory for this particular profile, inside of the saves dir
        profile_dir = os.path.join(profiles_dir, name)
        logging.debug(f"profile directory for {name} is {profile_dir}")

        for option in ["mods", "storage"]:
            if os.path.isfile(os.path.join(profile_dir,f"{option}-compressed.zip")):
                logging.info(f"Found compressed {option} in {name}")
            else:
                directory = os.path.join(profile_dir, option)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    logging.debug(f"Created {directory} directory")

        self.name = name  # Save the name
        self.directory = profile_dir
        self.starbound_dir = starbound_dir
        self.workshop_dir = workshop_dir
        self.loaded = False
        logging.debug(f"Saved attributes for {name}")

    def clear_starbound(self):
        """Delete all of the profile specific stuff in the starbound and workshop folders"""
        logging.debug(f"Call to clear_starbound() in profile {self.name}")
        if self.loaded:
            logging.warning("Attempt to clear starbound while this profile is loaded! Asking user for confirmation.")
            print(
                f"{Fore.YELLOW}Clearing Starbound directory while profile {self.name} is loaded! Are you sure you "
                f"want to procede? (Y/N)")
            if "y" not in input(f"{Fore.RED}THIS WILL CLEAR THIS PROFILE").lower():
                logging.info("Starbound directory clear aborted")
                return
        for directory in ["mods", "storage"]:
            for d in [os.path.join(self.starbound_dir, directory)]:
                if os.path.exists(d): shutil.rmtree(d)
            logging.info('Deleted Starbound "mods" and "storage" folders')

    def load(self):
        """Load this profile into the starbound install"""
        logging.info(f"Loading profile {self.name}...")

        # First, inflate any compressed profile data
        self.unpack()

        self.clear_starbound()
        for directory in ["mods", "storage"]:
            shutil.move(os.path.join(self.directory, directory), self.starbound_dir)
        self.loaded = True
        logging.info(f"Profile {self.name} loaded into Starbound")

    def unload(self):
        """Basically update(), but sets loaded to False and clears the Starbound dir"""
        if not self.loaded:
            logging.warning("Attempt to unload non-loaded profile, ignoring!")
            return
        logging.info(f"Unloading profile {self.name}...")
        print(f"{Fore.GREEN}Unloading {self.name}...")
        self.update(ignore_workshop=True)
        self.loaded = False
        self.clear_starbound()
        print(f"{Fore.GREEN}Unloaded {self.name}")
        logging.info(f"Unloaded profile {self.name}")

    def update(self, ignore_workshop=False):
        """Update this profile with the current starbound data"""
        if not self.loaded:
            logging.warning(f"Attempt to update profile {self.name} while not loaded! Asking user for confirmation")
            if "y" not in input(
                    f"{Fore.YELLOW}Profile {self.name} is not currently loaded.\nAre you sure you want to update it? (Y/N) ").lower():
                logging.info("Profile update aborted by user")
                return
        else:
            logging.debug(f"Updating loaded profile {self.name}")

        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
            logging.debug(f"Deleted profile directory for {self.name} for the purpose of a profile update")

        print(f"{Fore.GREEN}Updating {self.name}...")
        # This next chunk bothers me.
        # I feel like I should be able to get it done with one try/except and
        # iterate through the types, but right now I lack the brainpower
        # TODO: Clean this up!
        try:  # Mods
            shutil.move(os.path.join(self.starbound_dir, "mods"), os.path.join(self.directory, "mods"))
            logging.debug("Moved mods folder to profile folder")
        except FileNotFoundError:
            logging.warning("Failed to move mods folder to profile folder; the Starbound folder does not have a mods "
                            "folder!")
            print(f"{Fore.RED}Failed to update mods: Mods folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory, "mods")):
                os.makedirs(os.path.join(self.directory, "mods"))
                logging.debug(f"Creating empty mods directory for profile {self.name}")

        try:  # Storage
            shutil.move(os.path.join(self.starbound_dir, "storage"), os.path.join(self.directory, "storage"))
            logging.debug("Moved storage folder to profile folder")
        except FileNotFoundError:
            logging.warning("Failed to move storage folder to profile folder; the Starbound folder does not have a "
                            "storage folder!")
            print(f"{Fore.RED}Failed to update storage: Storage folder not found in starbound folder.")
            if not os.path.exists(os.path.join(self.directory, "storage")):
                os.makedirs(os.path.join(self.directory, "storage"))
                logging.debug(f"Creating empty storage directory for profile {self.name}")

        # Now for the hard part, workshop mods
        # Workshop mods are stored inside of the workshop_dir in folders with numerical names
        # Inside of those folders are files named contents.pak
        # First, we want to ask if we should include these workshop mods in the profile
        # If so, we should move the .pak s to our mods folder, and rename them
        # to workshop-mod-(numerical id)
        if ignore_workshop:
            logging.info(f"Ignoring Steam Workshop mods, finished updating profile {self.name}")
            return

        logging.info("Checking for workshop mods...")

        if len(next(os.walk(self.workshop_dir))[1]) > 0:
            logging.info(f"Found workshop mods, asking user if they should be included in profile {self.name}")
            if "y" not in input(
                    f"{Fore.YELLOW}Steam Workshop mods detected, would you like to add them to the profile?{Style.RESET_ALL} (Y/N) ").lower():
                print(f"{Fore.GREEN}Steam workshop mods ignored")
                print(f"{Fore.GREEN}Updated {self.name}")
                logging.info(f"Ignoring Steam Workshop mods, finished updating profile {self.name}")
                return

            for name in next(os.walk(self.workshop_dir))[1]:
                # Basically for numerically id-ed folder
                if not os.path.isfile(os.path.join(self.workshop_dir, name, "contents.pak")):
                    print(f"{Fore.YELLOW}No contents.pak found in workshop mod {name}")
                    logging.warning(f"No contents.pak file was found in workshop mod {name}")
                else:
                    shutil.move(
                        os.path.join(self.workshop_dir, name, "contents.pak"),
                        os.path.join(self.directory, "mods", f"workshop-mod-{name}.pak")
                    )
                    print(f"Installed workshop mod {name}")
                    logging.info("Moved workshop mod {name} to {self.name}\"s mod folder")

            print(f"{Fore.GREEN}Workshop mods added to profile, please unsubscribe from them")
            print(f"{Fore.GREEN}Updated {self.name}")

        else:
            logging.info("No workshop mods found")
        logging.info(f"Finished updating {self.name}")

    def compress(self):
        """Compress the save"s data"""
        if self.loaded:
            logging.warning("Attempt to compress loaded profile! Ignoring!")
            return
        if not settings["compress-profiles"]:
            logging.info("Call to Profile.compress() with compress-profiles false, ignoring!")
        logging.info(f"Compressing profile {self.name}")
        for option in ["mods", "storage"]:
            if os.path.exists(os.path.join(self.directory, option)):
                logging.debug(f"Creating archive {option}-compressed.zip")
                shutil.make_archive(
                    os.path.join(self.directory, f"{option}-compressed"),
                    "zip",
                    os.path.join(self.directory, option)
                    # ,logger=logging  # Having shutil log to our log adds thousands of lines of
                    # 2021-07-30 14:26:18,729: INFO - shutil - _make_zipfile: adding "starbound.config"
                    # so uhh, not sure we want that...
                )
                logging.debug(f"Deleting {option} folder for profile {self.name}")
                shutil.rmtree(os.path.join(self.directory, option))  # Delete the non-compressed stuff
            else:
                logging.warning(f"{option} folder not found to zip in profile {self.name}!")

    def unpack(self):
        """Inflate <name>.zip back to the "mods" and "storage" folders"""
        logging.info(f"Attempting to unpack profile {self.name}")
        for option in ["mods","storage"]:

            zipped_file = os.path.join(self.directory, f"{option}-compressed.zip")
            dest_dir = os.path.join(self.directory, option)

            if not os.path.isfile(zipped_file):
                logging.info(f"No compressed {option} zip found for {self.name}, ignoring")

            if os.path.exists(dest_dir):
                # There is already a folder for the unpacked data, abort
                logging.warning(f"Unpacking {self.name} {option} would overwrite existing {option} directory. Aborting!")
                return

            # Now that we know we won"t be overwriting anything and that the archive DOES
            # actually exist, we can go ahead and unpack
            shutil.unpack_archive(
                zipped_file,
                dest_dir,
                "zip",
            )
            logging.info(f"Extracted {option}-compressed.zip to {option} folder")
            os.remove(zipped_file)
            logging.info(f"Deleted {option}-compressed.zip in profile {self.name}")

    def delete(self):
        """Delete all files relating to this profile"""
        logging.info(f"Deleting data for profile {self.name}")
        if self.loaded:
            logging.warning(f"Deleting profile {self.name} while profile is loaded! This is probably an error!")
            print(f"{Fore.RED}WARNING: Deleting profile while profile is loaded!")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = os.path.join(script_dir, "profiles")
        shutil.rmtree(os.path.join(profiles_dir, self.name))
        self.loaded = False
        logging.info(f"Deleted profile {self.name}")
