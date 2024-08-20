# Pose Bone Transforms
Lightweight Blender addon to quickly setup both proportion deltas and procedural bones in Source 1

*Supports both legacy 2.79 and 2.8+ (all the way up to 4.x), download appropriate version of script*

## Copy Pose Bone Transforms
Copies a bone's parent space translation or rotation coordinates to the clipboard for procedural bone setup \
(also available in [SourceOps](https://github.com/bonjorno7/SourceOps))

1.  Select a bone in Pose Mode
2.  Pose Context Menu (w) > Copy Parent Translation/Rotation
3.  Paste from clipboard

## Copy Rotations From Other Armature
Transfer rotations of bones with matching names from one armature in the scene to another (for proportions "hack") \
This is performed by creating Copy Rotation modifiers for each matching bone on the target armature

1.  Select the target armature in Pose Mode
2.  Pose Context Menu (w) > Copy Rotations From Other Armature
3.  You can change the source armature in the dialogue box that appears on the bottom left of the 3D view
4.  **Apply Pose as Rest Pose** and **Clear Pose Constraints** to finalize (or just export as an animation)
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
