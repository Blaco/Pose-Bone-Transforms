# Pose Bone Transforms
Lightweight Blender addon to quickly setup both proportion deltas and procedural bones in Source 1

*Supports both legacy 2.79 and 2.8+ (all the way up to 4.x), download appropriate version of script*

## Copy Parent Translation/Rotation
Copies a bone's parent space translation or rotation coordinates to the clipboard **(for procedural bone setup)** \
(also available in [SourceOps](https://github.com/bonjorno7/SourceOps))

1.  Select a bone in Pose Mode
2.  Pose Context Menu (w) > Copy Parent Translation/Rotation
3.  Paste from clipboard

## Copy Transforms From Other Armature
Transfer transforms of bones with matching names from one armature in the scene to another **(for proportions trick)** \
This is performed by creating Copy Rotation/Location/Scale constraints for each bone on the target armature

1.  Select the target armature in Pose Mode
2.  Pose Context Menu (w) > Copy Transforms From Other Armature
3.  You can change the source armature and constraint type in the pop up dialogue box
4.  Select "Apply as Visual Transform" to directly apply the transform as a pose without creating constraints
5.  Select "Only Selected" to target only the currently selected bones in Pose Mode
6.  Select "Clear Previous" to remove existing COPY constraints before applying the transform
## Installation
    1. Go to Edit > Preferences
    2. Go to the Add-ons tab
    3. Click the `Install...` button in the top-right corner of the window
    4. Select the pose_bone_transforms.py file you downloaded, then click `Install Add-on`
    5. Activate the addon by checking the box next to the addon name
    6. Save startup preferences

## Links
- [Valve Developer Wiki - Procedural Bones](https://developer.valvesoftware.com/wiki/$proceduralbones)
- [Guide on how to setup procedural bones using this method](https://steamcommunity.com/sharedfiles/filedetails/?id=2415253996)
- [Guide on the basics of how to setup a proportions delta](https://steamcommunity.com/sharedfiles/filedetails/?id=2308084980) (for Gmod but applies to any branch)

## Credits
- [bonjorno7](https://github.com/bonjorno7/SourceOps)  (parent space math referenced from SourceOps)
