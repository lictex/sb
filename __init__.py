import nodeitems_utils
import importlib
import sys

bl_info = {
    "name": "sb",
    "author": "lictex_",
    "version": (0, 1, 0),
    "blender": (3, 5, 0),
    "description": "sb",
    "category": "Render",
}


def register_module(c):
    if hasattr(c, "classes"):
        for clazz in c.classes:
            import bpy
            bpy.utils.register_class(clazz)
    if hasattr(c, "register"):
        c.register()
    if hasattr(c, "nodes"):
        return [(t, n.bl_idname) for t, n in c.nodes]
    return []


def unregister_module(c):
    if hasattr(c, "unregister"):
        c.unregister()
    if hasattr(c, "classes"):
        for clazz in c.classes:
            import bpy
            bpy.utils.unregister_class(clazz)


module_names = [
    "nodes_seg",
    "nodes_normal",
    "nodes_depth",
    "nodes_pose",
    "nodes_send",
    "overlays_pose",
    "panels_pose",
    "panels_image",
    "utils",
    "api",
    "preferences",
]
modules: dict


if "bpy" not in locals():
    modules = [
        importlib.import_module(f".{m}", __package__)
        for m in module_names
    ]
else:
    for m, _ in filter(lambda x: x[1] in locals(), zip(modules, module_names)):
        importlib.reload(m)


class ShaderNodeSDCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


class CompositorNodeSDCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CompositorNodeTree'


def register():
    try:
        shader_nodes = []
        compositor_nodes = []
        for c in modules:
            r = register_module(c)
            shader_nodes.extend(
                n for _, n in filter(lambda r: r[0] == "SHADER", r)
            )
            compositor_nodes.extend(
                n for _, n in filter(lambda r: r[0] == "COMPOSITOR", r)
            )

        nodeitems_utils.register_node_categories("SD", [
            ShaderNodeSDCategory("SHADER_NODE_SD", "Stable Diffusion", items=[
                nodeitems_utils.NodeItem(x) for x in shader_nodes
            ]),
            CompositorNodeSDCategory("COMPOSITOR_NODE_SD", "Stable Diffusion", items=[
                nodeitems_utils.NodeItem(x) for x in compositor_nodes
            ]),
        ])
    except BaseException as e:
        unregister()
        importlib.import_module(__name__)
        raise e


def unregister():
    try:
        nodeitems_utils.unregister_node_categories("SD")
    except:
        pass

    for c in modules:
        try:
            unregister_module(c)
        except:
            pass

    for v in [x[0] for x in sys.modules.items()]:
        try:
            if v.startswith(__name__):
                del sys.modules[v]
        except:
            pass


if __name__ == "__main__":
    register()
