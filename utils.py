import bpy
import math
import os


def OpenPoseOverlayTypeProperty(*, name="OpenPose Overlay Type"):
    return bpy.props.EnumProperty(
        name=name,
        default="BODY",
        items=[
            ("NONE", "None", "None"),
            ("BODY", "Body", "Body"),
            ("FULL", "Full", "Full"),
        ],
    )


def OpenPoseOverlayThicknessProperty(*, name="OpenPose Overlay Thickness"):
    return bpy.props.FloatProperty(
        name=name,
        min=0,
        default=2,
    )


def EnumStringStoreProperty(**k):
    """ @`EnumStringProperty` """
    return bpy.props.StringProperty(
        **k,
        options=k.get("options", set()).union({"HIDDEN"}),
    )


def EnumStringProperty(*, sid, **k):
    """
    store enum as value string instead of index
    so inserting entries wont break existing selections
    """

    def _items(self) -> list[tuple[str, str, str]]:
        items = k["items"]
        if callable(items):
            items = items(self, bpy.context)
        return items

    def _find(self, o) -> int:
        return next((
            i for i, x in enumerate(_items(self))
            if x[0] == o
        ), -1)

    def _get(self):
        if s := self.get(sid):
            i = _find(self, s)
            if i == -1:
                return 2147483647
        else:
            i = _find(self, k.get("default", _items(self)[0][0]))

        assert i >= 0
        return i

    def _set(self, value):
        self[sid] = _items(self)[value][0]

    return bpy.props.EnumProperty(
        **k,
        get=_get,
        set=_set,
        options=k.get("options", set()).union({"SKIP_SAVE"}),
    )


def LongProperty(*, id, **k):
    """ long int in string property """

    def _get(self):
        return self.get(id, str(k.get("default", 0)))

    def _set(self, value):
        try:
            int(value)
            self[id] = value
        except:
            pass

    return bpy.props.StringProperty(
        get=_get,
        set=_set,
        **k | {
            "default": str(k.get("default", 0)),
        },
    )


def RoundedIntProperty(*, id, **kwargs):
    """ int property with step=8 """

    def update(self, _):
        try:
            setattr(
                self,
                id,
                int(round(getattr(self, id) / 8)) * 8
            ),
        except:
            pass

    return bpy.props.IntProperty(
        **kwargs,
        update=update,
    )


class CustomNode(bpy.types.NodeCustomGroup):
    cnode_type: str

    def init(self, context):
        self.init_node_tree()

    def free(self):
        if self.node_tree and self.node_tree.users == 1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)

    def copy(self, node):
        self.init_node_tree()

    def init_node_tree(
        self, *,
        inputs: tuple[str, str], outputs: tuple[str, str],
        pick_input: int = None, place_input: int = None,
    ):
        if not self.node_tree:
            self.node_tree = bpy.data.node_groups.new(
                f"._{os.urandom(16).hex()}",
                self.cnode_type
            )
        self.node_tree.nodes.clear()

        def update_sockets(ng_list, new):
            while len(ng_list) > len(new):
                ng_list.remove(ng_list[-1])
            for i, (ty, n) in enumerate(new):
                if i < len(ng_list):
                    oc = ng_list[i]
                    if oc.bl_socket_idname != ty:
                        ng_list.remove(oc)
                        ng_list.new(ty, n)
                        ng_list.move(len(ng_list) - 1, i)
                    else:
                        oc.name = n
                else:
                    ng_list.new(ty, n)

        if (pick_input, place_input) != (None, None):
            node_tree: bpy.types.NodeTree = bpy.context.space_data.node_tree
            prev_links = sorted(
                ((
                    next(
                        i for i, x in enumerate(self.inputs)
                        if x == ln.to_socket
                    ),
                    ln,
                    ln.from_socket,
                ) for ln in (
                    x for x in node_tree.links
                    if x.to_node == self
                )),
                key=lambda x: x[0],
            )
            for _, ln, _ in prev_links:
                try:
                    node_tree.links.remove(ln)
                except:
                    pass

        update_sockets(self.node_tree.inputs, inputs)

        # try to relink input sockets
        if (pick_input, place_input) != (None, None):
            if pick_input is None:
                pick_input = len(inputs)
            elif place_input is None:
                place_input = len(inputs)
            ofs = int(math.copysign(1, place_input - pick_input))
            a = min(place_input, pick_input)
            b = max(place_input, pick_input)

            def link(a, b):
                if s := next((x[2] for x in prev_links if x[0] == a), None):
                    node_tree.links.new(
                        s, self.inputs[b]
                    )
            for i in range(len(inputs)):
                if i == place_input:
                    if pick_input < len(inputs):
                        link(pick_input, place_input)
                elif a <= i <= b:
                    link(i+ofs, i)
                else:
                    link(i, i)

        update_sockets(self.node_tree.outputs, outputs)

        for input in [*self.inputs, *self.node_tree.inputs]:
            input.hide_value = True


class CustomShaderNode(bpy.types.ShaderNodeCustomGroup, CustomNode):
    cnode_type = 'ShaderNodeTree'


class CustomCompositorNode(bpy.types.CompositorNodeCustomGroup, CustomNode):
    cnode_type = 'CompositorNodeTree'


class NodeOperator(bpy.types.Operator):
    node_path: bpy.props.StringProperty()

    @property
    def node(self) -> bpy.types.Node:
        return bpy.data.path_resolve(
            self.node_path
            .removeprefix("bpy.data.")
            .replace("'", '"')
        )

    @classmethod
    def ui(cls, self, layout, **args):
        layout.operator(
            cls.bl_idname,
            **args,
        ).node_path = repr(self)


class ReinitializeNode(bpy.types.Operator):
    bl_idname = 'sd.reinit_node'
    bl_label = 'Reinitialize Node'
    bl_description = "WARNING: this will remove all links"

    def execute(self, context):
        context.active_node.free()
        context.active_node.init_node_tree()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return isinstance(context.active_node, CustomNode)


def menu(self, context):
    if ReinitializeNode.poll(context):
        layout = self.layout
        layout.separator()
        layout.operator(ReinitializeNode.bl_idname)


def register():
    bpy.types.NODE_MT_context_menu.append(menu)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(menu)


classes = [ReinitializeNode]
