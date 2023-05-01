import bpy
import gpu
import numpy
from . import utils
from . import overlays_pose


class RenderOpenPoseOverlay(utils.NodeOperator):
    bl_idname = "sd.render_openpose_overlay"
    bl_label = "Render OpenPose Overlay"

    def execute(self, context):
        if not self.node:
            return {"CANCELLED"}

        self.node.render(context)

        return {'FINISHED'}


class CompositorNodeOpenPose(utils.CustomCompositorNode):
    bl_idname = 'CompositorNodeSDOpenPose'
    bl_label = 'OpenPose'

    scene: bpy.props.PointerProperty(
        type=bpy.types.Scene,
        name="Scene"
    )

    def view_layers(self, context):
        return [
            (str(i), v.name, "")
            for i, v in enumerate(self.scene.view_layers)
        ]
    view_layer_index: bpy.props.EnumProperty(
        name="View Layer",
        items=view_layers
    )
    overlay: utils.OpenPoseOverlayTypeProperty()
    overlay_thickness: utils.OpenPoseOverlayThicknessProperty()

    def draw_buttons(self, context, layout):
        layout = layout.column()
        layout.template_ID(self, "scene")
        if self.scene:
            layout.prop(self, "view_layer_index")
            if 0 <= int(self.view_layer_index) < len(self.scene.view_layers):
                layout.prop(self, "overlay", text="Type")
                layout.prop(self, "overlay_thickness", text="Thickness")
                RenderOpenPoseOverlay.ui(
                    self, layout,
                    text="Render",
                )

    def init_node_tree(self, **k):
        super().init_node_tree(
            inputs=[],
            outputs=[
                ('NodeSocketColor', "Color")
            ],
            **k,
        )

        img = self.node_tree.nodes.new("CompositorNodeImage")
        output = self.node_tree.nodes.new("NodeGroupOutput")

        self.node_tree.links.new(
            img.outputs[0],
            output.inputs["Color"],
        )

    def render(self, context: bpy.types.Context):
        openpose_scene = overlays_pose.collect_parts(
            self.scene,
            self.scene.view_layers[
                int(self.view_layer_index)
            ]
        )

        size, _ = overlays_pose.scene_camera_info()
        offscreen = gpu.types.GPUOffScreen(*size, format="RGBA32F")
        with offscreen.bind():
            gpu_buf = gpu.state.active_framebuffer_get()
            gpu_buf.clear(color=(0.0, 0.0, 0.0, 1.0))
            overlays_pose.draw_overlay(
                offscreen_scene=openpose_scene,
                ty=self.overlay,
                thickness=self.overlay_thickness,
            )

            buf = gpu_buf.read_color(0, 0, *size, 4, 0, 'FLOAT')
            buf = numpy.array(buf, dtype=numpy.float32).T.flat.copy()

        offscreen.free()

        name = f"._OpenPose_{self.scene.name}_{self.scene.view_layers[int(self.view_layer_index)].name}"

        img = bpy.data.images.get(name) or bpy.data.images.new(
            name, *size, is_data=True
        )
        img.scale(*size)
        img.pixels = buf
        img.is_runtime_data = True

        next(filter(
            lambda x: x.bl_idname == "CompositorNodeImage",
            self.node_tree.nodes
        )).image=img


classes = [
    CompositorNodeOpenPose,
    RenderOpenPoseOverlay,
]


nodes = [
    ("COMPOSITOR", CompositorNodeOpenPose)
]
