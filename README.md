# PyMultibound
 Yet another Multibound-ish thing for Starbound.
 This lets you create and manage Starbound "profiles"
 letting you easily control what mods and what universe
 are active at what time.

Although it is stable enough that I use it, it is a work in progress and **probably has  MANY BUGS.** If you find a bug, please report it on the GitHub page.

## Steam Workshop support
PyMultibound supports steam workshop mods as part of profiles, but not in a conventional manner. 
On a profile update it scans the currently installed workshop mods, and if you select `yes` when prompted it will take the `contents.pak`
of each mod, rename it to `workshop-mod-<id>.pak` and group it with the manually installed mods. 
It is then safe to unsubscribe to your subscribed workshop mods; they are now part of the profile and will be loaded when the profile is selected.

## How it Works
PyMultibound creates snapshots of the `storage` and `mods` folders of Starbound, and saves them in "profiles" - a directory in the same  location as the scripts.

The default mode is `use-sbinit: true` in `settings.json`. In  this mode it will edit the selected profile's `sbinit.config` file, adding the `mods` and `storage` folders to the asset and storage directory fields in the init file. It then replaces Starbound's `sbinit.config` with this custom one, switching them back once Starbound exists.
In this mode PyMultibound will generate a fresh `sbinit.config` for each profile, meaning sbinits are profile-specific.


Originally PyMultibound did not edit `sbinit.config` and instead manually moved the `mods` and `storage` folders of each profile. It can take a while with large installs/many mods. This mode can be enabled by setting `use-sbinit` to `false` in the config.

## Character Appearance Editor
### THIS FEATURE IS EXPERIMENTAL, MAKE BACKUPS BEFORE USING
PyMultibound has a feature in which one can make appearance "templates" from pre-existing characters, and apply them to other characters. It works by replacing the `content/identity/` section of the .player file with the one from the template. As of now it does not update quest portraits, I may add this later. 

## Mac/Linux
Theoretically this should work for Mac and Linux users as well as Windows, with a few small directory changes in `util.py`. I can't test this, however, and there may be many issues.