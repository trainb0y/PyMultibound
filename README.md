# PyMultibound

### WIP Rewrite. Some old features are still missing! (CLI, Profile Compression)

[Chucklefish Forum Post](https://community.playstarbound.com/threads/pymultibound.168887/)

Yet another Multibound-ish thing for Starbound. This lets you create and manage Starbound "profiles" letting you easily control what mods and what universe are active at what time. (Basically different saves)

Although it is stable enough that I use it, it is a work in progress and probably has MANY, MANY BUGS. If you find a bug, please report it on the GitHub page.

Note that for now it requires Starbound to be installed through Steam to correctly function. This will hopefully change in the future.

## How to Use
Run `PyMultibound/gui.py`
Requires a recent Python(3) version and PyQt5 (Tested on 3.9 and 3.10)  
Packaged executables and/or an install script coming soon:tm:  
Note: Currently `cli.py` does nothing, will eventually have a command-line interface

## Steam Workshop support

PyMultibound supports steam workshop mods as part of profiles, but not in a conventional manner. On profile creation, it optionally scans the currently installed workshop mods, and takes the contents.pak of each mod, renames it to `workshop-<name>-<version>.pak` and groups it with the manually installed mods. It is then safe to unsubscribe to your subscribed workshop mods; they are now part of the profile and will be loaded when the profile is selected.

More advanced workshop support will be coming soon.

## How it Works

PyMultibound creates snapshots of the storage and mods folders of Starbound, and saves them in "profiles" - a directory in the same location as the scripts. It then starts Starbound with a profile-specific sbinit.config that directs Starbound to the profile's files.

## Mac/Windows
Although I can only test this on Linux, I've tried to make it support Windows too. If there are any issues when using Windows, please report it as a bug.

I have no way to test on a Mac, and it probably won't work out of the box. Chances are most of `paths.py` would have to be changed.

## Character Appearance Editor
PyMultibound has a feature in which one can make appearance "templates" from pre-existing characters, and apply them to other characters. It works by replacing the `content/identity/` section of the `.player` file with the one from the template. As of now it does not update quest portraits, I may add this later.

Note that this feature is experimental, please make a backup before using it.

## Contributing
Check out CONTRIBUTING.md
