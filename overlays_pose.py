import colorsys
import gpu_extras.presets
import gpu_extras.batch
import gpu
import bpy
import numpy
import collections
from . import preferences


vs = '''
    uniform mat4 tfm;
    uniform vec2 size;
    uniform vec3 start;
    uniform vec3 end;
    uniform float width;

    in vec2 position;
    out vec2 coord;
    out float z;

    vec3 proj(vec3 w) {
        vec4 h = tfm * vec4(w, 1.0f);
        float z = h.z;
        return vec3(h.xy / h.w * size, z);
    }
    void main() {
        coord = position - 0.5f;

        vec2 pos = position - 0.5f;

        vec3 pp = proj(start);
        vec2 p = pp.xy;
        vec3 pt = proj(end);
        vec2 t = pt.xy;

        if(p != t){
            pos.y *= width;
            pos.x += 0.5f;
            pos.x *= distance(t, p);
            vec2 direction = normalize(t - p);
            float angle = atan(direction.y, direction.x);
            mat3 rot = mat3(
                cos(angle), -sin(angle), 0.0f,
                sin(angle), cos(angle), 0.0f,
                0.0f, 0.0f, 1.0f
            );
            pos = (vec3(pos, 1.0f) * rot).xy;
        } else {
            pos *= width;
        }
        pos += p;
        z = min(pt.z, pp.z);
        gl_Position = vec4(pos / size, 0.0f, 1.0f);
    }
'''

fs = '''
    uniform float gamma;
    uniform vec3 col;
    uniform int rect;

    in vec2 coord;
    in float z;
    out vec4 color;

    void main()
    {
        if(z < 0.0f) {
            discard;
        }
        color.rgb = col;
        color.rgb = pow(color.rgb, vec3(gamma));
        if(rect == 0) color.a = length(coord - vec2(0.0f)) > 0.5f ? 0.0f : 1.0f;
        else color.a = 1.0f;
    }
'''

shader = gpu.types.GPUShader(vs, fs)
batch = gpu_extras.batch.batch_for_shader(shader, 'TRIS', {
    "position": [(1, 1), (0, 1), (0, 0),
                 (1, 1), (0, 0), (1, 0)]
})


# from https://github.com/lllyasviel/ControlNet-v1-1-nightly/blob/b9ae087ef56ca786d9a3ee1008f814bb171bb913/annotator/openpose/util.py#L75
parts_color = [
    [255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0],
    [170, 255, 0], [85, 255, 0], [0, 255, 0], [0, 255, 85],
    [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255],
    [0, 0, 255], [85, 0, 255], [170, 0, 255], [255, 0, 255],
    [255, 0, 170], [255, 0, 85]
]
parts_link = [
    [1, 2], [1, 5], [2, 3], [3, 4],
    [5, 6], [6, 7], [1, 8], [8, 9],
    [9, 10], [1, 11], [11, 12], [12, 13],
    [1, 0], [0, 14], [14, 16], [0, 15],
    [15, 17]
]
hand_parts_link = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [0, 9], [9, 10], [10, 11], [11, 12],
    [0, 13], [13, 14], [14, 15], [15, 16],
    [0, 17], [17, 18], [18, 19], [19, 20]
]


def scene_camera_info():
    size = [
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y
    ]
    mat = bpy.context.scene.camera.calc_matrix_camera(
        depsgraph=bpy.context.evaluated_depsgraph_get(),
        x=bpy.context.scene.render.resolution_x,
        y=bpy.context.scene.render.resolution_y,
        scale_x=bpy.context.scene.render.pixel_aspect_x,
        scale_y=bpy.context.scene.render.pixel_aspect_y,
    ) @ bpy.context.scene.camera.matrix_world.inverted()
    return size, mat


viewport_state = None
viewport_openpose_scene = {
    "bodies": [],
    "faces": [],
    "hands": [],
}


def draw_overlay(*, offscreen_scene=None, ty="FULL", thickness=2):
    if not offscreen_scene:
        if not bpy.context.space_data.overlay.show_overlays:
            return

        size = [bpy.context.region.width, bpy.context.region.height]
        mat = bpy.context.region_data.perspective_matrix
        thickness = preferences.get().openpose_overlay_thickness
        ty = preferences.get().openpose_overlay

        refresh_viewport_parts()

        openpose_scene = viewport_openpose_scene
    else:
        size, mat = scene_camera_info()
        openpose_scene = offscreen_scene

    def draw_link(a, b, col, *, rect=False, width=8):
        gpu.state.blend_set("ALPHA")
        shader.bind()
        shader.uniform_float("tfm", mat)
        shader.uniform_float("size", size)
        shader.uniform_float("start", a)
        shader.uniform_float("end", b)
        shader.uniform_float("col", col)
        shader.uniform_float("width", width * thickness)
        shader.uniform_int("rect", 1 if rect else 0)
        shader.uniform_float("gamma", 2.2 if not openpose_scene else 1)
        batch.draw(shader)

    if ty == "NONE":
        return
    for body in openpose_scene["bodies"]:
        for i, ln in enumerate(parts_link):
            a, b = [body.get(x) for x in ln]
            if a and b:
                draw_link(
                    a, b,
                    numpy.array(parts_color[int(i)]) / 255 * 0.6
                )

        for i, pt in body.items():
            draw_link(pt, pt, numpy.array(parts_color[int(i)]) / 255)

    if ty == "BODY":
        return

    for hand in openpose_scene["hands"]:
        for i, ln in enumerate(hand_parts_link):
            a, b = [hand.get(x) for x in ln]
            if a and b:
                draw_link(
                    a, b,
                    colorsys.hsv_to_rgb(
                        i / float(len(hand_parts_link)),
                        1.0,
                        1.0
                    ),
                    rect=True,
                    width=2,
                )

        for i, pt in hand.items():
            draw_link(pt, pt, [0, 0, 1])

    for face in openpose_scene["faces"]:
        for pt in face:
            draw_link(pt, pt, [1, 1, 1], width=6)


def collect_body(obj):
    out = {}
    for bone, pose in filter(
        lambda x: x[0].sd_openpose.body_binding,
        zip(obj.data.edit_bones or obj.data.bones, obj.pose.bones)
    ):
        for x in bone.sd_openpose.body_binding:
            out[x.index] = obj.matrix_world @ pose.head.lerp(
                pose.tail, x.offset
            )
    return out


def collect_face(obj):
    out = []
    for bone, pose in filter(
        lambda x: x[0].sd_openpose.face_binding,
        zip(obj.data.edit_bones or obj.data.bones, obj.pose.bones)
    ):
        for x in bone.sd_openpose.face_binding:
            out.append(obj.matrix_world @ pose.head.lerp(
                pose.tail, x.offset
            ))
    return out


def collect_hands(obj):
    l = collections.defaultdict(dict)
    for bone, pose in filter(
        lambda x: x[0].sd_openpose.hand_binding,
        zip(obj.data.edit_bones or obj.data.bones, obj.pose.bones)
    ):
        for x in bone.sd_openpose.hand_binding:
            l[x.group][x.index] = obj.matrix_world @ pose.head.lerp(
                pose.tail, x.offset
            )
    return l.values()


def collect_parts(scene: bpy.types.Scene, view_layer: bpy.types.ViewLayer):
    openpose_scene = {
        "bodies": [],
        "faces": [],
        "hands": [],
    }

    for obj in (
        x for x in scene.objects
        if x.type == "ARMATURE" and x.visible_get(view_layer=view_layer)
    ):
        openpose_scene["bodies"].append(collect_body(obj))
        openpose_scene["faces"].append(collect_face(obj))
        openpose_scene["hands"].extend(collect_hands(obj))

    return openpose_scene


def refresh_viewport_parts(*, force=False):
    global viewport_openpose_scene, viewport_state
    current_state = bpy.context.scene, bpy.context.view_layer
    if (not force) and (viewport_state == current_state):
        return

    viewport_state = current_state
    viewport_openpose_scene = collect_parts(
        *current_state
    )

    for x in filter(lambda x: x.type == 'VIEW_3D', bpy.context.screen.areas):
        x.tag_redraw()


@bpy.app.handlers.persistent
def update_handler(scene, context):
    refresh_viewport_parts(force=True)


def draw_overlay_options(self, context):
    row = self.layout.row(align=True)
    row.prop(preferences.get(), "openpose_overlay", text="OpenPose")
    row.prop(preferences.get(), "openpose_overlay_thickness", text="Thickness")


def register():
    global overlay_handle
    overlay_handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_overlay, (), "WINDOW", "POST_PIXEL"
    )
    bpy.app.handlers.depsgraph_update_post.append(update_handler)
    bpy.types.VIEW3D_PT_overlay.append(draw_overlay_options)


def unregister():
    bpy.types.VIEW3D_PT_overlay.remove(draw_overlay_options)
    bpy.app.handlers.depsgraph_update_post.remove(update_handler)
    bpy.types.SpaceView3D.draw_handler_remove(overlay_handle, "WINDOW")
