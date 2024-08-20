import bpy
import math

bl_info = {
    "name": "Pose Bone Transforms (Source Engine)",
    "description": "Get parent space transforms of the active bone (vrd), Copy rotations from other armatures (proportions)",
    "author": "bonjorno7, Taco",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Pose > Pose Specials (W-Key)",
    "wiki_url": "https://github.com/Blaco/Pose-Bone-Transforms",
    "category": "Animation",
}

class CopyPoseBoneTransforms(bpy.types.Operator):
    bl_idname = 'pose.copy_bone_transforms'
    bl_label = 'Copy Pose Bone Transforms'
    bl_description = 'Copy parent space transforms of the active pose bone to clipboard'
    bl_options = {'REGISTER'}

    type = bpy.props.EnumProperty(
        name='Transform Type',
        items=(
            ('TRANSLATION', 'Translation', ''),
            ('ROTATION', 'Rotation', ''),
        ),
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' and context.active_pose_bone is not None

    def execute(self, context):
        bone = context.active_pose_bone

        if bone.parent:
            parent_matrix = bone.parent.matrix.inverted_safe()
            bone_matrix = parent_matrix * bone.matrix
        else:
            bone_matrix = bone.matrix

        if self.type == 'ROTATION':
            vector = bone_matrix.to_euler()
            vector = [math.degrees(angle) for angle in vector]
        else:
            vector = bone_matrix.to_translation()

        result_string = ' '.join([str(round(value, 6)) for value in vector])
        context.window_manager.clipboard = result_string

        self.report({'INFO'}, '{}: {}'.format(self.type.capitalize(), result_string))
        return {'FINISHED'}

class ApplyCopyRotationConstraints(bpy.types.Operator):
    bl_idname = "pose.apply_copy_rotation_constraints"
    bl_label = "Copy Rotation Constraints"
    bl_description = 'Copy rotations on matching bone names from another armature in the scene'
    bl_options = {'REGISTER', 'UNDO'}

    source_armature = bpy.props.EnumProperty(
        items=lambda self, context: [(obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == 'ARMATURE'],
        name="Source Armature"
    )

    def execute(self, context):
        source_armature_name = self.source_armature
        target_armature = context.active_object

        # Ensure we have valid armatures selected
        if not source_armature_name or not target_armature or target_armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select a valid source armature and target armature.")
            return {'CANCELLED'}

        source_armature = bpy.data.objects[source_armature_name]

        # Add Copy Rotation constraints to matching bones on the target armature
        for bone in source_armature.pose.bones:
            if bone.name in target_armature.pose.bones:
                target_bone = target_armature.pose.bones[bone.name]

                constraint = target_bone.constraints.new('COPY_ROTATION')
                constraint.target = source_armature
                constraint.subtarget = bone.name

        bpy.context.scene.update()
        self.report({'INFO'}, "Copy Rotation Constraints applied. Apply Pose as Rest Pose and Clear Pose Constraints to finalize.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "source_armature", text="Source Armature")

def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Translation').type = 'TRANSLATION'
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Rotation').type = 'ROTATION'
    self.layout.operator(ApplyCopyRotationConstraints.bl_idname, text='Copy Rotations From Other Armature')

def specials_menu_func(self, context):
    self.layout.separator()
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Translation').type = 'TRANSLATION'
    self.layout.operator(CopyPoseBoneTransforms.bl_idname, text='Copy Parent Rotation').type = 'ROTATION'
    self.layout.operator(ApplyCopyRotationConstraints.bl_idname, text='Copy Rotations From Other Armature')

def register():
    bpy.utils.register_class(CopyPoseBoneTransforms)
    bpy.utils.register_class(ApplyCopyRotationConstraints)
    bpy.types.VIEW3D_MT_pose.append(menu_func)
    bpy.types.VIEW3D_MT_pose_specials.append(specials_menu_func)

def unregister():
    bpy.utils.unregister_class(CopyPoseBoneTransforms)
    bpy.utils.unregister_class(ApplyCopyRotationConstraints)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)
    bpy.types.VIEW3D_MT_pose_specials.remove(specials_menu_func)

if __name__ == "__main__":
    register()
