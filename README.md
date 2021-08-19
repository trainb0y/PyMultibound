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

When you choose a profile, it deletes the contents of the folders and replaces them with the contents of the selected profile.  
(This is the default mode, and is somewhat bug-low)

I was told that I could do it all by modifying the `sbinit.config` file instead of moving the folders. 
A basic system for this is implemented, but it is probably very buggy. I recommend using this mode only if moving the profiles takes an intolerably long time.   
(Can be enabled by setting `"use-sbinit": true` in `settings.json`)

In the `sbinit` mode PyMultibound will generate a fresh `sbinit.config` for each profile, meaning sbinits are profile-specific.

## Mac/Linux
Theoretically this should work for Mac and Linux users as well as Windows. It should only require changing `steamapps-directory` in the settings, but I can't test it.