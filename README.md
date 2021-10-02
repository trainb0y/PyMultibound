# PyMultibound

Yet another Multibound-ish thing for Starbound. This lets you create and manage Starbound "profiles"
letting you easily control what mods and what universe are active at what time.

Although it is stable enough that I use it, it is a work in progress and **probably has MANY BUGS.** If you find a bug,
please report it on the GitHub page.

## Steam Workshop support

PyMultibound supports steam workshop mods as part of profiles, but not in a conventional manner. On profile creation it
optionally scans the currently installed workshop mods, and takes the `contents.pak`
of each mod, renames it to `workshop-mod-<id>.pak` and groups it with the manually installed mods. It is then safe to
unsubscribe to your subscribed workshop mods; they are now part of the profile and will be loaded when the profile is
selected.

## How it Works

PyMultibound creates snapshots of the `storage` and `mods` folders of Starbound, and saves them in "profiles" - a
directory in the same location as the scripts. It then starts Starbound with a profile-specific `sbinit.config` that
directs Starbound to the profile's files.

## Character Appearance Editor

### THIS FEATURE IS EXPERIMENTAL, MAKE BACKUPS BEFORE USING

PyMultibound has a feature in which one can make appearance "templates" from pre-existing characters, and apply them to
other characters. It works by replacing the `content/identity/` section of the .player file with the one from the
template. As of now it does not update quest portraits, I may add this later.

## Mac/Linux
This currently works on Windows and Linux. If you're on Linux, you'll have to change the `steamapps-directory` field of 
`settings.json` to match your steamapps directory, as it defaults to
the default Windows location.

I have no way to test on a Mac, and it probably won't work out of the box.
Chances are most of `util.py` would have to be changed.