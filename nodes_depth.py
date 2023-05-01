from . import utils


class CompositorNodeDepth(utils.CustomCompositorNode):
    bl_idname = 'CompositorNodeSDDepth'
    bl_label = 'Depth Postprocess'

    def init_node_tree(self, **k):
        super().init_node_tree(
            inputs=[
                ('NodeSocketFloat', "Depth")
            ],
            outputs=[
                ('NodeSocketColor', "Color")
            ],
            **k,
        )

        input = self.node_tree.nodes.new("NodeGroupInput")
        norm = self.node_tree.nodes.new("CompositorNodeNormalize")
        inv = self.node_tree.nodes.new("CompositorNodeInvert")
        output = self.node_tree.nodes.new("NodeGroupOutput")

        self.node_tree.links.new(
            input.outputs["Depth"],
            norm.inputs[0],
        )
        self.node_tree.links.new(
            norm.outputs[0],
            inv.inputs["Color"],
        )
        self.node_tree.links.new(
            inv.outputs[0],
            output.inputs["Color"],
        )


classes = [
    CompositorNodeDepth,
]


nodes = [
    ("COMPOSITOR", CompositorNodeDepth)
]
