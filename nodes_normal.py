from . import utils


class ShaderNodeNormal(utils.CustomShaderNode):
    bl_idname = 'ShaderNodeSDNormal'
    bl_label = 'ControlNet Normal'

    def init_node_tree(self, **k):
        super().init_node_tree(
            inputs=[],
            outputs=[
                ('NodeSocketColor', "Color")
            ],
            **k,
        )

        geom = self.node_tree.nodes.new("ShaderNodeNewGeometry")
        tfm = self.node_tree.nodes.new("ShaderNodeVectorTransform")
        tfm.vector_type = 'VECTOR'
        tfm.convert_from = 'WORLD'
        tfm.convert_to = 'CAMERA'
        math = self.node_tree.nodes.new("ShaderNodeVectorMath")
        math.operation = 'MULTIPLY_ADD'
        math.inputs[1].default_value = [-0.5, 0.5, -0.5]
        math.inputs[2].default_value = [0.5, 0.5, 0.5]
        output = self.node_tree.nodes.new("NodeGroupOutput")

        self.node_tree.links.new(
            geom.outputs["Normal"],
            tfm.inputs["Vector"],
        )
        self.node_tree.links.new(
            tfm.outputs["Vector"],
            math.inputs["Vector"],
        )
        self.node_tree.links.new(
            math.outputs["Vector"],
            output.inputs["Color"],
        )


class CompositorNodeNormal(utils.CustomCompositorNode):
    bl_idname = 'CompositorNodeSDNormal'
    bl_label = 'Normal Postprocess'

    def init_node_tree(self, **k):
        super().init_node_tree(
            inputs=[
                ('NodeSocketColor', "AOV Output")
            ],
            outputs=[
                ('NodeSocketColor', "Color")
            ],
            **k,
        )

        input = self.node_tree.nodes.new("NodeGroupInput")
        blend = self.node_tree.nodes.new("CompositorNodeAlphaOver")
        blend.inputs[1].default_value = [0.5, 0.5, 1.0, 1.0]
        output = self.node_tree.nodes.new("NodeGroupOutput")

        self.node_tree.links.new(
            input.outputs["AOV Output"],
            blend.inputs[2],
        )
        self.node_tree.links.new(
            blend.outputs[0],
            output.inputs["Color"],
        )


classes = [
    ShaderNodeNormal, CompositorNodeNormal
]


nodes = [
    ("SHADER", ShaderNodeNormal),
    ("COMPOSITOR", CompositorNodeNormal)
]
