# PyMultibound
 Yet another Multibound-ish thing for Starbound.
 This lets you create and manage Starbound "profiles"
 letting you easily control what mods and what universe
 are active at what time.

Although it is stable enough that I use it, it is a work in progress and **probably has  MANY BUGS.** If you find a bug, please report it on the GitHub page.

## How it Works
It works by creating snapshots "profiles" of the `storage` and `mods` folders of Starbound, and saving them as a profile.

When you choose a profile, it deletes the contents of the folders and replaces it with the contents of the selected profile.

(See the help option in the main menu for details)

## Steam Workshop support
PyMultibound supports steam workshop mods as part of profiles, but not in a conventional manner. 
On a profile update it scans the currently installed workshop mods, and if you select `yes` when prompted it will take the `contents.pak`
of each mod, rename it to `workshop-mod-\<id\>.pak and group it with the manually installed mods. 
It is then safe to unsubscribe to your subscribed workshop mods; they are now part of the profile
