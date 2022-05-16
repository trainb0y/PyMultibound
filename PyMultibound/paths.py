import os, platform, logging, sys
from os.path import join


# About the two sbinits:
# When I switched to Linux I noticed the sbinit.config looked different.
# I'm not sure if this is normal or if its something I did, but I figured I might as
# well put it here.
#
# ...it also crashes without this
blankWindowsSBInit = {
    "assetDirectories": [
        "..\\assets\\",
        "..\\mods\\"
    ],

    "storageDirectory": "..\\storage\\",

    "defaultConfiguration": {
        "gameServerBind": "*",
        "queryServerBind": "*",
        "rconServerBind": "*"
    }
}
blankLinuxSBInit = {
    "assetDirectories": [
        "../assets/",
        "../mods/"
    ],

    "storageDirectory": "../storage/"
}


profilesDir = join(os.path.dirname(os.path.realpath(__file__)), os.pardir,
                   "profiles")  # Directory in which the profiles reside
templatesDir = join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "templates")
temporaryPath = join(templatesDir, "temp")

if platform.system() == "Windows":
    steamappsDir = os.path.join(*["c:\\", "Program Files (x86)", "Steam", "steamapps"])

    starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
    workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
    dumpJson = join(starboundDir, "win32", "dump_versioned_json.exe")  # path to the dump_versioned_json.exe
    makeJson = join(starboundDir, "win32", "make_versioned_json.exe")  # path to the make_versioned_json.exe
    starboundExecutable = join(starboundDir, "win64", "starbound.exe")
    unpackAssets = join(starboundDir, "win64", "asset_unpacker.exe")
    blankSBInit = blankWindowsSBInit

elif platform.system() == "Linux":
    steamappsDir = os.path.join(os.path.expanduser("~/.local/share/Steam/steamapps"))

    starboundDir = join(steamappsDir, "common", "Starbound")  # Main Starbound directory inside of steamapps
    workshopDir = join(steamappsDir, "workshop", "content", "211820")  # Directory for starbound's workshop mods
    starboundExecutable = join(starboundDir, "linux", "run-client.sh")
    dumpJson = join(starboundDir, "linux", "dump_versioned_json")  # path to the dump_versioned_json.exe
    makeJson = join(starboundDir, "linux", "make_versioned_json")  # path to the make_versioned_json.exe
    unpackAssets = join(starboundDir, "linux", "asset_unpacker")
    blankSBInit = blankLinuxSBInit

else:
    logging.critical("Unrecognized platform, unable to find steamapps directory")
    sys.exit()
