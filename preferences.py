import bpy
from . import api
from . import utils


class ClearCaches(bpy.types.Operator):
    bl_idname = f"sd.clear_enum_caches"
    bl_label = f"Clear Enum Caches"

    def execute(self, context):
        api.clear_enum_caches()
        return {'FINISHED'}


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    url: bpy.props.StringProperty(
        name="Stable Diffusion WebUI URL",
        update=lambda x, y: api.clear_enum_caches()
    )

    openpose_overlay: utils.OpenPoseOverlayTypeProperty()
    openpose_overlay_thickness: utils.OpenPoseOverlayThicknessProperty()

    def draw(self, context):
        layout = self.layout.column()
        layout.prop(self, "url")
        layout.prop(self, "openpose_overlay")
        layout.prop(self, "openpose_overlay_thickness")
        layout.operator(ClearCaches.bl_idname)


def get(*, context=bpy.context) -> Preferences:
    return context.preferences.addons[__package__].preferences


classes = [
    ClearCaches, Preferences,
]
