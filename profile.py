import json
import os, shutil, logging
from os.path import join

import util
from util import Style, Fore, Back, load_settings

settings = util.load_settings()  # I know this means it gets called multiple


# times per run, but its a small little file operation and shouldn"t really matter


class Profile:

    def create(self, name, starbound_dir, workshop_dir):
        logging.info(f"Creating profile with name {name}, sb dir {starbound_dir} and workshop dir {workshop_dir}")
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

        if settings["use-sbinit"]:
            if not os.path.isfile(join(profile_dir, "sbinit.config")):
                with open(join(profile_dir, "sbinit.config"), "x") as f:
                    json.dump(util.blank_sbinit, f, indent=2)
                    logging.info(f"Created blank sbinit.config for {name}")
            else:
                logging.info(f"Found existing sbinit.config for {name}")

        self.name = name  # Save the name
        self.directory = profile_dir
        self.starbound_dir = starbound_dir
        self.workshop_dir = workshop_dir
        self.loaded = False
        logging.debug(f"Saved attributes for {name}")

    def clear_starbound(self):
        """Delete all of the profile specific stuff in the starbound and workshop folders"""
        logging.debug(f"Call to clear_starbound() in profile {self.name}")
        if settings["use-sbinit"]:
            logging.critical("Attempted to clear Starbound, but we're set to use sbinit.config!")
            raise Exception("Attempted to clear Starbound, but we're set to use sbinit.config! This is a critical bug!")

        if self.loaded:
            logging.warning("Attempt to clear starbound while this profile is loaded! Asking user for confirmation.")
            print(
                f"{Fore.YELLOW}Clearing Starbound directory while profile {self.name} is loaded! Are you sure you "
                f"want to procede? (Y/N)")
            if "y" not in input(f"{Fore.RED}THIS WILL CLEAR THIS PROFILE").lower():
                logging.info("Starbound directory clear aborted")
                return
        for directory in ["mods", "storage"]:
            for d in [join(self.starbound_dir, directory)]:
                if os.path.exists(d): shutil.rmtree(d)
            logging.info('Deleted Starbound "mods" and "storage" folders')

    def load(self):
        """Load this profile into the starbound install"""
        logging.info(f"Loading profile {self.name}...")

        # First, inflate any compressed profile data
        self.unpack()

        if settings["use-sbinit"]:
            logging.info(f"Loading {self.name} using sbinit.config")
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
                print()
                print("Will attempt to load profile by moving files...")

                logging.warning("Attempted to load profile using sbinit but no sbinit.config found for this profile!")
                logging.info("Attempting to load profile by moving files...")

                settings["use-sbinit"] = False
                self.load()
                settings["use-sbinit"] = True
                return False

            # Take the current sbinit.config, add our
            # storage folder and mods folder

            # DONT DELETE THIS PROFILE'S SBINIT.CONFIG
            # in case the user has custom stuff in there.
            # we don't really want to have to deal with undoing
            # this, it's easier just to leave it

            logging.debug("Loading data from profile's sbinit...")
            try:
                with open(join(self.directory, "sbinit.config"), "r") as f:
                    sbinit = json.load(f)
                    logging.debug("Got data from sbinit")
            except Exception as e:
                logging.error(f"Error reading {self.name}'s sbinit.config': {e}")
                return False

            sbinit["assetDirectories"].append(join(self.directory, "mods"))
            sbinit["storageDirectory"] = join(self.directory, "storage")
            logging.debug("Edited sbinit data")



            util.safe_move(
                join(self.starbound_dir, settings["starbound"], "sbinit.config"),
                join(self.directory, "sbinit-original.config")
            )
            logging.info("Moved sbinit.config to sbinit-original.config")

            with open(join(self.starbound_dir, settings["starbound"], "sbinit.config"), "x") as sb:
                json.dump(sbinit, sb)
                self.loaded = True
                logging.info("Replaced Starbound's sbinit.config")
                return True


        else:
            logging.info(f"Loading {self.name} by moving files, not sbinit.config!")
            # Actually move the files
            self.clear_starbound()
            for directory in ["mods", "storage"]:
                util.safe_move(join(self.directory, directory), self.starbound_dir)
            self.loaded = True
            logging.info(f"Profile {self.name} loaded into Starbound")
            return True

    def unload(self):
        """Basically update(), but sets loaded to False and clears the Starbound dir"""
        if not self.loaded:
            logging.warning("Attempt to unload non-loaded profile, ignoring!")
            return
        if settings["use-sbinit"]:
            logging.info("Replacing Starbound's sbinit.config with original")
            util.safe_move(
                join(self.directory,"sbinit-original.config"),
                join(self.starbound_dir, settings["starbound"], "sbinit.config")
            )
            logging.info("Replaced Starbound's sbinit.config")
            self.loaded = False

        else:
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
            util.safe_move(join(self.starbound_dir, "mods"), join(self.directory, "mods"))
            logging.debug("Moved mods folder to profile folder")
        except FileNotFoundError:
            logging.warning("Failed to move mods folder to profile folder; the Starbound folder does not have a mods "
                            "folder!")
            print(f"{Fore.RED}Failed to update mods: Mods folder not found in starbound folder.")
            if not os.path.exists(join(self.directory, "mods")):
                os.makedirs(join(self.directory, "mods"))
                logging.debug(f"Creating empty mods directory for profile {self.name}")

        try:  # Storage
            util.safe_move(join(self.starbound_dir, "storage"), join(self.directory, "storage"))
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
                if not os.path.isfile(join(self.workshop_dir, name, "contents.pak")):
                    print(f"{Fore.YELLOW}No contents.pak found in workshop mod {name}")
                    logging.warning(f"No contents.pak file was found in workshop mod {name}")
                else:
                    util.safe_move(
                        join(self.workshop_dir, name, "contents.pak"),
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
        if self.loaded:
            logging.warning("Attempt to compress loaded profile! Ignoring!")
            return
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
        if self.loaded:
            logging.warning(f"Deleting profile {self.name} while profile is loaded! This is probably an error!")
            print(f"{Fore.RED}WARNING: Deleting profile while profile is loaded!")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.rmtree(self.directory)
        self.loaded = False
        logging.info(f"Deleted profile {self.name}")
