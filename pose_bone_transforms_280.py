import bpy
import math

bl_info = {
    "name": "Pose Bone Transforms (Source Engine)",
    "description": "Get parent space transforms of the active bone (vrd), Copy rotations from other armatures (proportions)",
    "author": "bonjorno7, Taco",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Pose Context Menu",
    "warning": "",
    "category": "Animation",
}

class CopyPoseBoneTransforms(bpy.types.Operator):
    bl_idname = 'pose.copy_bone_transforms'
    bl_label = 'Copy Pose Bone Transforms'
    bl_description = 'Copy parent space transforms of the active pose bone to clipboard'
    bl_options = {'REGISTER', 'INTERNAL'}

    type: bpy.props.EnumProperty(
        name='Transform Type',
        items=[
            ('TRANSLATION', 'Translation', ''),
            ('ROTATION', 'Rotation', ''),
        ],
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        bone = context.active_pose_bone

        if bone is None:
            self.report({'INFO'}, 'No active bone')
            return {'CANCELLED'}

        if bone.parent:
            parent = bone.parent.matrix.inverted_safe()
            matrix = parent @ bone.matrix
        else:
            matrix = bone.matrix

        if self.type == 'ROTATION':
            vector = matrix.to_euler()
            vector = [math.degrees(n) for n in vector]
        else:
            vector = matrix.to_translation().xyz

        string = ' '.join(str(round(n, 6)) for n in vector)
        context.window_manager.clipboard = string

        self.report({'INFO'}, f'{self.type.capitalize()}: {string}')
        return {'FINISHED'}

class ApplyCopyRotationConstraints(bpy.types.Operator):
    bl_idname = "pose.apply_copy_rotation_constraints"
    bl_label = "Copy Rotation Constraints"
    bl_description = 'Copy rotations on matching bone names from another armature in the scene'
    bl_options = {'REGISTER', 'UNDO'}

    source_armature: bpy.props.EnumProperty(
        name="Source Armature",
        items=lambda self, context: [(obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == 'ARMATURE'],
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE' and context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context: bpy.types.Context) -> set:
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

        bpy.context.view_layer.update()
        self.report({'INFO'}, "Copy Rotation Constraints applied. Apply Pose as Rest Pose and Clear Pose Constraints to finalize.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "source_armature", text="Source Armature")

def menu_func(self, context: bpy.types.Context):
    layout = self.layout
    layout.separator()
    layout.operator('pose.copy_bone_transforms', text='Copy Parent Translation').type = 'TRANSLATION'
    layout.operator('pose.copy_bone_transforms', text='Copy Parent Rotation').type = 'ROTATION'
    layout.operator('pose.apply_copy_rotation_constraints', text='Copy Rotations From Other Armature')

def register():
    bpy.utils.register_class(CopyPoseBoneTransforms)
    bpy.utils.register_class(ApplyCopyRotationConstraints)
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CopyPoseBoneTransforms)
    bpy.utils.unregister_class(ApplyCopyRotationConstraints)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
