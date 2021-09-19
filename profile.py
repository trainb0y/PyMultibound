import os, shutil, logging, copy, json
from os.path import join

from util import *


class Profile:

    def create(self, name, starbound_dir, workshop_dir):
        logging.info(f"Creating profile with name {name}")
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        profiles_dir = join(script_dir, "profiles")

        # Now we make a directory for this particular profile, inside of the saves dir
        profile_dir = join(profiles_dir, name)
        logging.debug(f"profile directory for {name} is {profile_dir}")

        for option in ["mods", "storage"]:
            if os.path.isfile(join(profile_dir, f"{option}-compressed.zip")):
                logging.info(f"Found compressed {option} in {name}")
            else:
                directory = join(profile_dir, option)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    logging.debug(f"Created {directory} directory")
                else:
                    logging.info(f"Found pre-existing {directory} directory")

        if not os.path.isfile(join(profile_dir, "sbinit.config")):
            with open(join(profile_dir, "sbinit.config"), "x") as f:
                sbinit = copy.deepcopy(blank_sbinit)
                sbinit["assetDirectories"].append(join(profile_dir, "mods"))
                sbinit["storageDirectory"] = join(profile_dir, "storage")
                print(sbinit)
                json.dump(sbinit, f, indent=2)
                logging.info(f"Created sbinit.config for {name}")
        else:
            logging.info(f"Found existing sbinit.config for {name}")
        self.directory = profile_dir
        self.name = name  # Save the name

    def load(self):
        """Load this profile into the starbound install"""
        logging.info(f"Loading profile {self.name}...")

        # First, inflate any compressed profile data
        self.unpack()
        if not os.path.isfile(join(self.directory, "sbinit.config")):
            # In all honesty we could just create a blank one here,
            # but this implies it was moved/deleted or there is a serious bug,
            # as there is no way use-sbinit could be false on profile creation
            # and be true here

            # ...and also I already wrote all of this before I thought
            # of just creating one :) -trainb0y1

            print(f"\n{Fore.RED}No sbinit.config found for profile {self.name}!")
            print("Either you moved or deleted it after you started this program, or this")
            print("is a bug, please report it (along with PyMultibound.log) on the GitHub!")
            print("https://github.com/trainb0y1/PyMultibound/issues\n")

            logging.warning("Attempted to load profile using sbinit but no sbinit.config found for this profile!")

            return False
        return True

    def get_starbound_data(self, starbound_dir, workshop_dir):
        """Update this profile with the current starbound data"""

        print(f"{Fore.GREEN}Replacing {self.name} with current Starbound data...")
        # This next chunk bothers me.
        # I feel like I should be able to get it done with one try/except and
        # iterate through the types, but right now I lack the brainpower
        # TODO: Clean this up!
        try:  # Mods
            util.safe_move(join(starbound_dir, "mods"), join(self.directory, "mods"))
            logging.debug("Moved mods folder to profile folder")
        except FileNotFoundError:
            logging.warning("Failed to move mods folder to profile folder; the Starbound folder does not have a mods "
                            "folder!")
            print(f"{Fore.RED}Failed to update mods: Mods folder not found in starbound folder.")
            if not os.path.exists(join(self.directory, "mods")):
                os.makedirs(join(self.directory, "mods"))
                logging.debug(f"Creating empty mods directory for profile {self.name}")

        try:  # Storage
            util.safe_move(join(starbound_dir, "storage"), join(self.directory, "storage"))
            logging.debug("Moved storage folder to profile folder")
        except FileNotFoundError:
            logging.warning("Failed to move storage folder to profile folder; the Starbound folder does not have a "
                            "storage folder!")
            print(f"{Fore.RED}Failed to update storage: Storage folder not found in starbound folder.")
            if not os.path.exists(join(self.directory, "storage")):
                os.makedirs(join(self.directory, "storage"))
                logging.debug(f"Creating empty storage directory for profile {self.name}")

        # Now for the hard part, workshop mods
        # Workshop mods are stored inside of the workshop_dir in folders with numerical names
        # Inside of those folders are files named contents.pak
        # First, we want to ask if we should include these workshop mods in the profile
        # If so, we should move the .pak s to our mods folder, and rename them
        # to workshop-mod-(numerical id)

        logging.info("Checking for workshop mods...")

        if len(next(os.walk(workshop_dir))[1]) > 0:
            logging.info(f"Found workshop mods, asking user if they should be included in profile {self.name}")
            if "y" not in input(
                    f"{Fore.YELLOW}Steam Workshop mods detected, would you like to add them to the profile?{Style.RESET_ALL} (Y/N) ").lower():
                print(f"{Fore.GREEN}Steam workshop mods ignored")
                print(f"{Fore.GREEN}Updated {self.name}")
                logging.info(f"Ignoring Steam Workshop mods, finished updating profile {self.name}")
                return

            for name in next(os.walk(workshop_dir))[1]:
                # Basically for numerically id-ed folder
                if not os.path.isfile(join(workshop_dir, name, "contents.pak")):
                    print(f"{Fore.YELLOW}No contents.pak found in workshop mod {name}")
                    logging.warning(f"No contents.pak file was found in workshop mod {name}")
                else:
                    util.safe_move(
                        join(workshop_dir, name, "contents.pak"),
                        join(self.directory, "mods", f"workshop-mod-{name}.pak")
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
        if not settings["compress-profiles"]:
            logging.info("Call to Profile.compress() with compress-profiles false, ignoring!")
        logging.info(f"Compressing profile {self.name}")
        for option in ["mods", "storage"]:
            if os.path.exists(join(self.directory, option)):
                logging.debug(f"Creating archive {option}-compressed.zip")
                shutil.make_archive(
                    join(self.directory, f"{option}-compressed"),
                    "zip",
                    join(self.directory, option)
                    # ,logger=logging  # Having shutil log to our log adds thousands of lines of
                    # 2021-07-30 14:26:18,729: INFO - shutil - _make_zipfile: adding "starbound.config"
                    # so uhh, not sure we want that...
                )
                logging.debug(f"Deleting {option} folder for profile {self.name}")
                shutil.rmtree(join(self.directory, option))  # Delete the non-compressed stuff
            else:
                logging.warning(f"{option} folder not found to zip in profile {self.name}!")

    def unpack(self):
        """Inflate <name>.zip back to the "mods" and "storage" folders"""
        logging.info(f"Attempting to unpack profile {self.name}")
        for option in ["mods", "storage"]:

            zipped_file = join(self.directory, f"{option}-compressed.zip")
            dest_dir = join(self.directory, option)

            if not os.path.isfile(zipped_file):
                logging.info(f"No compressed {option} zip found for {self.name}, ignoring")
                return  # fixes dumb warning from next check

            if os.path.exists(dest_dir):
                # There is already a folder for the unpacked data, abort
                logging.warning(
                    f"Unpacking {self.name} {option} would overwrite existing {option} directory. Aborting!")
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
        shutil.rmtree(self.directory)
        logging.info(f"Deleted profile {self.name}")
