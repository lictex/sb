import bpy
from . import overlays_pose


mapping = [
    "Nose",
    "Neck",
    "RShoulder",
    "RElbow",
    "RWrist",
    "LShoulder",
    "LElbow",
    "LWrist",
    "RHip",
    "RKnee",
    "RAnkle",
    "LHip",
    "LKnee",
    "LAnkle",
    "REye",
    "LEye",
    "REar",
    "LEar",
]

hand_mapping = [
    "Root",
    *(
        f"{a}, {b}"
        for a in range(5)
        for b in range(1, 5)
    ),
]

prev_op_values = {}


def update(*t):
    def impl(self, _):
        if t:
            global prev_op_values
            prev_op_values[t[0]] = getattr(self, t[1])
        overlays_pose.refresh_viewport_parts(force=True)
    return impl


class FaceBindingProperty(bpy.types.PropertyGroup):
    offset: bpy.props.FloatProperty(
        name="Offset",
        min=0,
        max=1,
        update=update(),
    )


class HandBindingProperty(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(
        name="Index",
        default=-1,
        update=update(),
    )

    group: bpy.props.IntProperty(
        name="Group",
        update=update("hand_group", "group"),
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        min=0,
        max=1,
        update=update(),
    )


class BodyBindingProperty(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty(
        name="Index",
        default=-1,
        update=update(),
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        min=0,
        max=1,
        update=update(),
    )


class OpenPoseProperty(bpy.types.PropertyGroup):
    body_binding: bpy.props.CollectionProperty(
        name="Body Binding",
        type=BodyBindingProperty,
    )
    active_body_binding_index: bpy.props.IntProperty()
    hand_binding: bpy.props.CollectionProperty(
        name="Hand Binding",
        type=HandBindingProperty,
    )
    active_hand_binding_index: bpy.props.IntProperty()
    face_binding: bpy.props.CollectionProperty(
        name="Face Binding",
        type=FaceBindingProperty,
    )
    active_face_binding_index: bpy.props.IntProperty()


class BindingList(bpy.types.UIList):
    bl_idname = "SD_UL_OpenPoseBinding"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if isinstance(item, FaceBindingProperty):
            layout.label(text=f"Face @ {item.offset}")
        elif isinstance(item, BodyBindingProperty):
            layout.label(text=f"{mapping[item.index]} @ {item.offset}")
        elif isinstance(item, HandBindingProperty):
            layout.label(text=f"{hand_mapping[item.index]} @ {item.offset}")


def def_binding_ops(ty, mapping=None, read_prev=dict()):
    class BindingAdd(bpy.types.Operator):
        bl_idname = f"sd.add_openpose_{ty.lower()}_binding"
        bl_label = f"Add {ty} Binding"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            b = getattr(
                context.active_bone.sd_openpose,
                f"{ty.lower()}_binding"
            )
            i = b.add()
            setattr(
                context.active_bone.sd_openpose,
                f"active_{ty.lower()}_binding_index",
                len(b) - 1
            )
            if mapping:
                i.index = int(self.index)
            for k, v in read_prev.items():
                if c := prev_op_values.get(k):
                    setattr(
                        i, v,
                        c
                    )
            overlays_pose.refresh_viewport_parts(force=True)
            return {'FINISHED'}

        if mapping:
            bl_property = "index"
            index: bpy.props.EnumProperty(items=tuple([
                (str(i), n, n)
                for i, n in enumerate(mapping)
            ]))

            def invoke(self, context, event):
                wm = context.window_manager
                wm.invoke_search_popup(self)
                return {'FINISHED'}

    class BindingRemove(bpy.types.Operator):
        bl_idname = f"sd.remove_openpose_{ty.lower()}_binding"
        bl_label = f"Remove {ty} Binding"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            getattr(
                context.active_bone.sd_openpose,
                f"{ty.lower()}_binding"
            ).remove(
                getattr(
                    context.active_bone.sd_openpose,
                    f"active_{ty.lower()}_binding_index"
                )
            )
            overlays_pose.refresh_viewport_parts(force=True)
            return {'FINISHED'}

        @classmethod
        def poll(cls, context):
            return getattr(
                context.active_bone.sd_openpose,
                f"active_{ty.lower()}_binding_index"
            ) in range(len(
                getattr(
                    context.active_bone.sd_openpose,
                    f"{ty.lower()}_binding"
                )
            ))
    return {"Add": BindingAdd, "Remove": BindingRemove}


BindingOps = {
    "Body": def_binding_ops("Body", mapping),
    "Hand": def_binding_ops("Hand", hand_mapping, read_prev={"hand_group": "group"}),
    "Face": def_binding_ops("Face"),
}


class OpenPosePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_sd_openpose"
    bl_label = "OpenPose Binding"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    def draw(self, context):
        layout = self.layout.column()
        prop = context.active_bone.sd_openpose

        def draw_list(ty):
            layout.label(text=f"{ty} Binding:")
            r = layout.row()
            r.template_list(
                BindingList.bl_idname,
                "",
                prop,
                f"{ty.lower()}_binding",
                prop,
                f"active_{ty.lower()}_binding_index"
            )
            l = r.column(align=True)
            l.operator(BindingOps[ty]["Add"].bl_idname, icon="ADD", text="")
            l.operator(
                BindingOps[ty]["Remove"].bl_idname, icon="REMOVE", text=""
            )
            return (
                BindingOps[ty]["Remove"].poll(context)
                and
                getattr(
                    prop,
                    f"{ty.lower()}_binding"
                )[getattr(prop, f"active_{ty.lower()}_binding_index")]

            )
        if active := draw_list("Body"):
            layout.prop(active, "offset")
        layout.separator()
        if active := draw_list("Hand"):
            layout.prop(active, "group")
            layout.prop(active, "offset")
        layout.separator()
        if active := draw_list("Face"):
            layout.prop(active, "offset")

    @ classmethod
    def poll(cls, context):
        return isinstance(context.active_bone, bpy.types.EditBone)


def register():
    bpy.types.Bone.sd_openpose = bpy.props.PointerProperty(
        type=OpenPoseProperty
    )
    bpy.types.EditBone.sd_openpose = bpy.props.PointerProperty(
        type=OpenPoseProperty
    )


def unregister():
    del bpy.types.EditBone.sd_openpose
    del bpy.types.Bone.sd_openpose


classes = [
    BodyBindingProperty, HandBindingProperty, FaceBindingProperty, OpenPoseProperty,
    *(y for x in BindingOps.values() for y in x.values()),
    BindingList, OpenPosePanel,
]
