import bpy
import math
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
bl_info = {
    "name": "Pose Bone Transforms",
    "description": "Get parent space transforms of the active bone (vrd), Copy transforms from other armatures (proportions)",
    "author": "bonjorno7, Taco",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Pose Context Menu",
    "doc_url": "https://github.com/Blaco/Pose-Bone-Transforms",
    "category": "Animation",
}
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class CopyPoseBoneTransforms(bpy.types.Operator):
    """
    Copies the parent space transforms of the active pose bone to the clipboard.
    This operator allows users to copy either the translation or rotation values
    of the active pose bone in relation to its parent. The values are copied in
    the form of degrees for rotations or standard units for translation.
    """
    bl_idname = 'pose.copy_parent_bone_transforms'
    bl_label = 'Copy Parent Transforms'
    bl_description = 'Copy parent space transforms of the active pose bone to clipboard'
    bl_options = {'REGISTER', 'UNDO'}

    type: bpy.props.EnumProperty(
        name='Transform Type',
        items=[
            ('TRANSLATION', 'Translation', ''),
            ('ROTATION', 'Rotation', ''),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' or 'PAINT_WEIGHT' and context.active_pose_bone is not None

    def execute(self, context):
        bone = context.active_pose_bone
        if bone.parent:
            parent_matrix = bone.parent.matrix.inverted_safe()
            bone_matrix = parent_matrix @ bone.matrix
        else:
            bone_matrix = bone.matrix

        if self.type == 'ROTATION':
            vector = bone_matrix.to_euler()
            vector = [math.degrees(angle) for angle in vector]
        else:
            vector = bone_matrix.to_translation()

        result_string = ' '.join([str(round(value, 6)) for value in vector])
        context.window_manager.clipboard = result_string
        self.report({'INFO'}, f"{self.type.capitalize()}: {result_string}")  # Updated to use f-strings
        return {'FINISHED'}
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class ApplyCopyTransformsConstraints(bpy.types.Operator):
    """
    Applies copy transforms constraints from one armature to another based on matching bone names.

    This operator applies a specific type of constraint (rotation, location, scale, or transform)
    to matching bones between the target armature (the active armature) and the source armature
    selected by the user. The constraints copy transforms from the source armature to the target armature.

    If the "Apply as Visual Transform" option is selected, the constraints will be applied to the 
    target armature, followed by a visual transform application. All copy constraints from the source
    armature will then be removed from the target armature.
    """
    bl_idname = "pose.copy_transforms_from_other"
    bl_label = "Copy Transforms From Other Armature"
    bl_description = 'Copy transforms on matching bone names from another armature in the scene'
    bl_options = {'REGISTER', 'UNDO'}

    source_armature: bpy.props.EnumProperty(
        items=lambda self, context: [
            (obj.name, obj.name, "") for obj in bpy.data.objects
            if obj.type == 'ARMATURE' and obj != ApplyCopyTransformsConstraints.get_target_armature(context)], name="Source")
    
    constraint_type: bpy.props.EnumProperty(
        name="Constraint Type",
        items=[
            ('COPY_ROTATION', 'Copy Rotation', ''),
            ('COPY_LOCATION', 'Copy Location', ''),
            ('COPY_SCALE', 'Copy Scale', ''),
            ('COPY_TRANSFORMS', 'Copy Transforms', ''),
        ],
    )

    apply_visual_transform: bpy.props.BoolProperty(
        name="Apply as Visual Transform",
        description="Apply visual transforms to pose and clear created constraints",
        default=False)

    dialog_shown = False

    @classmethod
    def get_target_armature(cls, context):
        obj = context.active_object
        # Case 1: If the active object is an armature in Pose Mode, it's the target
        if obj and obj.type == 'ARMATURE' and obj.mode == 'POSE': return obj
        # Case 2: If in Weight Paint mode, find the armature linked to the mesh's Armature modifier
        if obj and obj.type == 'MESH' and context.mode == 'PAINT_WEIGHT':
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE' and mod.object:
                    return mod.object
        return None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        # Check if the active object is an armature in Pose mode
        if obj and obj.type == 'ARMATURE' and obj.mode == 'POSE':
            return True
        # Check if the active object is a mesh in Weight Paint mode with an associated armature in Pose mode
        if obj and obj.type == 'MESH' and context.mode == 'PAINT_WEIGHT':
            armature = cls.get_target_armature(context)
            return armature and armature.mode == 'POSE'
        return False

    def invoke(self, context, event):
        # Check if there's another armature in the scene, excluding the target armature
        target_armature = self.get_target_armature(context)
        other_armatures_exist = any(obj.type == 'ARMATURE' and obj != target_armature for obj in bpy.data.objects)

        if not other_armatures_exist:
            self.report({'ERROR'}, "No other armatures found in the scene.")
            return {'CANCELLED'}

        self.dialog_shown = True # Set the flag to True when the dialog is shown
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # If the dialog hasn't been shown yet, call invoke first
        if not self.dialog_shown:
            return self.invoke(context, None)

        # Get the target armature (either the active armature in Pose mode or the linked armature in Weight Paint mode)
        target_armature = self.get_target_armature(context)
        source_armature_name = self.source_armature

        # Ensure valid armatures are selected
        if not source_armature_name or not target_armature:
            self.report({'ERROR'}, "Requires a valid source armature and target armature.")
            return {'CANCELLED'}

        source_armature = bpy.data.objects[source_armature_name]

        # List to store tuples of (bone, constraint) for newly created constraints
        created_constraints = []

        # Add the selected constraint to matching bones on the target armature
        for bone in source_armature.pose.bones:
            if bone.name in target_armature.pose.bones:
                target_bone = target_armature.pose.bones[bone.name]

                # Remove any pre-existing constraints from the same source armature
                existing_constraints = [c for c in target_bone.constraints if c.type == self.constraint_type and c.target == source_armature]
                for constraint in existing_constraints:
                    target_bone.constraints.remove(constraint)

                # Create new constraint
                constraint = target_bone.constraints.new(self.constraint_type)
                constraint.target = source_armature
                constraint.subtarget = bone.name
                created_constraints.append((target_bone, constraint))  # Store bone and constraint

        # Apply visual transforms and remove constraints if the option is enabled
        if self.apply_visual_transform:

            # Apply the visual transforms to all bones on the armature
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.visual_transform_apply()

            # Clear the stored constraints created by this operation
            for bone, constraint in created_constraints:
                bone.constraints.remove(constraint)

            self.report({'INFO'}, "Visual Transform applied, constraints removed.")
        else:
            self.report({'INFO'}, f"{self.constraint_type.replace('_', ' ').title()} constraints applied.")  # Updated to use f-strings

        # Update the scene
        bpy.context.view_layer.update()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "source_armature", text="Source")
        layout.prop(self, "constraint_type", text="Type")
        layout.prop(self, "apply_visual_transform", text="Apply as Visual Transform")
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def context_menu_func(self, context):
    self.layout.separator()
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Translation').type = 'TRANSLATION'
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Rotation').type = 'ROTATION'
    self.layout.operator(ApplyCopyTransformsConstraints.bl_idname, text='Copy Transforms From Other Armature')
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def register():
    bpy.utils.register_class(CopyPoseBoneTransforms)
    bpy.utils.register_class(ApplyCopyTransformsConstraints)
    bpy.types.VIEW3D_MT_pose_context_menu.append(context_menu_func)

def unregister():
    bpy.utils.unregister_class(CopyPoseBoneTransforms)
    bpy.utils.unregister_class(ApplyCopyTransformsConstraints)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(context_menu_func)

if __name__ == "__main__":
    register()
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
