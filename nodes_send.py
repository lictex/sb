import bpy
import re
import os
import io
import json
import numpy
import tempfile
import base64
import threading
from . import api
from . import utils
from . import nodes_pose


class SDIMG2IMGProperty(bpy.types.PropertyGroup):
    resize_mode: bpy.props.EnumProperty(
        name="Resize Mode",
        items=[
            (str(id), name, name)
            for id, name in enumerate([
                "Just resize",
                "Crop and resize",
                "Resize and fill",
                "Just resize (latent upscale)",
            ])
        ],
    )
    use_inpaint: bpy.props.BoolProperty(
        name="Inpaint",
        update=lambda _, ctx: ctx.active_node.init_node_tree(),
    )
    mask_blur: bpy.props.IntProperty(
        name="Mask Blur",
        min=0,
        max=64,
        default=32,
    )
    inpainting_fill: bpy.props.EnumProperty(
        name="Fill",
        items=[
            (str(id), name, name)
            for id, name in enumerate([
                'fill',
                'original',
                'latent noise',
                'latent nothing',
            ])
        ],
    )
    inpaint_full_res: bpy.props.BoolProperty(name="Only Masked")
    inpaint_full_res_padding: utils.RoundedIntProperty(
        id="inpaint_full_res_padding",
        name="Padding",
        min=0,
        max=256,
        default=32,
    )


class SDTXT2IMGProperty(bpy.types.PropertyGroup):
    enable_hr: bpy.props.BoolProperty(name="HiRes")
    hr_scale: bpy.props.FloatProperty(
        name="Scale Factor",
        step=5,
        min=1,
        max=4,
    )
    hr_resize_x: utils.RoundedIntProperty(
        id="hr_resize_x",
        name="Target Width",
        min=0,
        max=2048,
    )
    hr_resize_y: utils.RoundedIntProperty(
        id="hr_resize_y",
        name="Target Height",
        min=0,
        max=2048,
    )
    hr_upscaler_s: utils.EnumStringStoreProperty()
    hr_upscaler: utils.EnumStringProperty(
        sid="hr_upscaler_s",
        name="Upscaler",
        items=api.HiResUpscalers,
    )
    hr_second_pass_steps: bpy.props.IntProperty(
        name="HiRes Steps",
        min=0,
        max=150,
    )


class SDProperty(bpy.types.PropertyGroup):
    denoising_strength: bpy.props.FloatProperty(
        name="Denoising Strength",
        min=0,
        max=1,
        default=0.7,
    )
    prompt: bpy.props.StringProperty(name="Prompt")
    negative_prompt: bpy.props.StringProperty(name="Negative Prompt")

    width: utils.RoundedIntProperty(
        id="width",
        name="Width",
        min=64,
        max=2048,
        default=512,
    )
    height: utils.RoundedIntProperty(
        id="height",
        name="Height",
        min=64,
        max=2048,
        default=512,
    )
    sampler_name_s: utils.EnumStringStoreProperty()
    sampler_name: utils.EnumStringProperty(
        sid="sampler_name_s",
        name="Sampler",
        items=api.Samplers,
    )
    steps: bpy.props.IntProperty(
        name="Steps",
        min=1,
        max=150,
        default=20,
    )
    cfg_scale: bpy.props.FloatProperty(
        name="CFG Scale",
        min=1,
        max=30,
        default=7,
    )

    seed: utils.LongProperty(
        id="seed",
        name="Seed",
        default=-1
    )
    seed_extras: bpy.props.BoolProperty(name="Extras")
    subseed: utils.LongProperty(
        id="subseed",
        name="Subseed",
        default=-1
    )

    subseed_strength: bpy.props.IntProperty(name="Subseed Strength")
    seed_resize_from_h: utils.RoundedIntProperty(
        id="seed_resize_from_h",
        name="Resize Seed Height",
        min=0,
        max=2048,
    )
    seed_resize_from_w: utils.RoundedIntProperty(
        id="seed_resize_from_w",
        name="Resize Seed Width",
        min=0,
        max=2048,
    )
    batch_size: bpy.props.IntProperty(
        name="Batch Size",
        min=1,
        max=8
    )
    n_iter: bpy.props.IntProperty(
        name="Batch Count",
        min=1,
        max=100
    )


class ControlNetPassProperty(bpy.types.PropertyGroup):
    model_s: utils.EnumStringStoreProperty()
    model: utils.EnumStringProperty(
        sid="model_s",
        name="Model",
        items=api.CNetModels,
        update=lambda _, ctx: ctx.active_node.init_node_tree()
    )

    use_mask: bpy.props.BoolProperty(name="Use Mask")
    srgb: bpy.props.BoolProperty(name="sRGB")

    weight: bpy.props.FloatProperty(
        name="Weight",
        min=0,
        max=2,
        default=1,
    )
    lowvram: bpy.props.BoolProperty(name="Low VRAM")
    guidance_start: bpy.props.FloatProperty(
        name="Guidance Start",
        min=0,
        max=1,
        default=0,
    )
    guidance_end: bpy.props.FloatProperty(
        name="Guidance End",
        min=0,
        max=1,
        default=1,
    )
    resize_mode: bpy.props.EnumProperty(
        name="Resize Mode",
        items=[
            (str(id), name, name)
            for id, name in enumerate([
                "Just Resize",
                "Scale to Fit (Inner Fit)",
                "Envelope (Outer Fit)",
            ])
        ],
    )
    control_mode: bpy.props.EnumProperty(
        name="Control Mode",
        items=[
            (str(id), name, name)
            for id, name in enumerate([
                "Balanced",
                "My prompt is more important",
                "ControlNet is more important",
            ])
        ],
    )

    module_s: utils.EnumStringStoreProperty()
    module: utils.EnumStringProperty(
        sid="module_s",
        name="Preprocessor",
        items=api.CNetModules,
    )
    pixel_perfect: bpy.props.BoolProperty(name="Pixel Perfect")
    processor_res: bpy.props.IntProperty(
        name="Preprocessor Resolution",
        min=64,
        max=2048,
        update=lambda self, _: setattr(
            self,
            "processor_res",
            self.processor_res//8*8
        ),
        default=512,
    )
    threshold_a: bpy.props.FloatProperty(
        name="A",
        default=1,
    )
    threshold_b: bpy.props.FloatProperty(
        name="B",
        default=1,
    )


class TiledVAEProperty(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled")
    encoder_tile_size: utils.RoundedIntProperty(
        id="encoder_tile_size",
        name="Encoder Tile Size",
        min=256,
        max=4096,
        default=960,
    )
    decoder_tile_size: utils.RoundedIntProperty(
        id="decoder_tile_size",
        name="Decoder Tile Size",
        min=48,
        max=512,
        default=64,
    )
    vae_to_gpu: bpy.props.BoolProperty(
        name="Move VAE to GPU",
        default=True,
    )
    fast_decoder: bpy.props.BoolProperty(
        name="Fast Decoder",
        default=True,
    )
    fast_encoder: bpy.props.BoolProperty(
        name="Fast Encoder",
        default=True,
    )
    color_fix: bpy.props.BoolProperty(name="Color Fix")


class ControlNetPassList(bpy.types.UIList):
    bl_idname = "SD_UL_ControlNetPassList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.model)


class ControlNetPassAdd(bpy.types.Operator):
    bl_idname = f"sd.add_control_net_pass"
    bl_label = "Add ControlNet Pass"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.active_node.control_net_passes.add()
        context.active_node.init_node_tree()
        return {'FINISHED'}

    @ classmethod
    def poll(cls, context):
        return (
            context.active_node.bl_idname == CompositorNodeSend.bl_idname
        )


class ControlNetPassRemove(bpy.types.Operator):
    bl_idname = f"sd.remove_control_net_pass"
    bl_label = "Remove ControlNet Pass"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node: CompositorNodeSend = context.active_node
        i = node.active_control_net_pass_index
        node.control_net_passes.remove(i)

        if node.ty == "IMAGE":
            i += 1  # the `scene color` input

        node.init_node_tree(pick_input=i)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_node.bl_idname == CompositorNodeSend.bl_idname
            and
            (
                0
                <= context.active_node.active_control_net_pass_index <
                len(context.active_node.control_net_passes)
            )
        )


def def_move_op(ty):
    class Move(bpy.types.Operator):
        bl_idname = f"sd.move_control_net_pass_{ty.lower()}"
        bl_label = f"Move ControlNet Pass {ty}"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):
            node: CompositorNodeSend = context.active_node
            src = node.active_control_net_pass_index
            dst = src-1 if ty == "Up" else src+1
            node.control_net_passes.move(src, dst)
            node.active_control_net_pass_index = dst
            if node.ty == "IMAGE":
                src += 1
                dst += 1
            node.init_node_tree(pick_input=src, place_input=dst)
            return {'FINISHED'}

        @classmethod
        def poll(cls, context):
            l = len(context.active_node.control_net_passes)
            return (
                context.active_node.bl_idname == CompositorNodeSend.bl_idname
                and
                (
                    (1 if ty == "Up" else 0)
                    <= context.active_node.active_control_net_pass_index <
                    (l if ty == "Up" else l-1)
                )
            )
    return Move


ControlNetPassMoveUp = def_move_op("Up")
ControlNetPassMoveDown = def_move_op("Down")


class CompositorNodeSend(utils.CustomCompositorNode):
    bl_idname = 'CompositorNodeSDSend'
    bl_label = 'Stable Diffusion'

    progress: bpy.props.IntProperty(
        name="Progress",
        subtype="PERCENTAGE",
        options={"SKIP_SAVE"},
        default=-1,
        soft_min=0,
        soft_max=100,
    )
    sd: bpy.props.PointerProperty(type=SDProperty)
    txt2img: bpy.props.PointerProperty(type=SDTXT2IMGProperty)
    img2img: bpy.props.PointerProperty(type=SDIMG2IMGProperty)
    ty: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("TEXT", "Text", "txt2img"),
            ("IMAGE", "Image", "img2img"),
        ],
        update=lambda self, ctx: ctx.active_node.init_node_tree(
            place_input=0 if self.ty == "IMAGE" else None,
            pick_input=0 if self.ty == "TEXT" else None,
        ),
    )
    control_net_passes: bpy.props.CollectionProperty(
        type=ControlNetPassProperty,
    )
    tiled_vae: bpy.props.PointerProperty(type=TiledVAEProperty)
    active_control_net_pass_index: bpy.props.IntProperty()

    def draw_buttons_ext(self, context, layout):
        layout = layout.column()

        r = layout.column(align=True)
        r.prop(self.sd, "prompt")
        r.prop(self.sd, "negative_prompt")

        r = layout.column(align=True)
        r.row(align=True).prop(self, "ty", expand=True)
        box = r.box().column()
        if self.ty == "IMAGE":
            box.prop(self.img2img, "resize_mode")
            box.prop(self.img2img, "use_inpaint")
            if self.img2img.use_inpaint:
                box = box.box().column()
                l = box.split(factor=0.333)
                l.prop(self.img2img, "inpaint_full_res")
                if self.img2img.inpaint_full_res:
                    l.prop(self.img2img, "inpaint_full_res_padding")
                box.prop(self.img2img, "mask_blur")
                box.prop(self.img2img, "inpainting_fill")
        else:
            box.prop(self.txt2img, "enable_hr")
            if self.txt2img.enable_hr:
                box = box.box().column(align=True)
                box.prop(self.txt2img, "hr_upscaler", text="")
                box.prop(self.txt2img, "hr_scale")
                box.prop(self.txt2img, "hr_second_pass_steps")
                x = box.split(factor=0.5, align=True)
                x.prop(self.txt2img, "hr_resize_x")
                x.prop(self.txt2img, "hr_resize_y")

        x = r.split(factor=0.5, align=True)
        x.prop(self.sd, "width")
        x.prop(self.sd, "height")

        r.prop(self.sd, "sampler_name", text="")
        r.prop(self.sd, "denoising_strength")

        x = r.split(factor=0.5, align=True)
        x.prop(self.sd, "steps")
        x.prop(self.sd, "cfg_scale")

        x = r.split(factor=0.5, align=True)
        x.prop(self.sd, "batch_size")
        x.prop(self.sd, "n_iter")

        x = r.split(factor=0.666, align=True)
        x.prop(self.sd, "seed", text="")
        x.prop(self.sd, "seed_extras", toggle=True)
        if self.sd.seed_extras:
            box = r.box().column(align=True)
            x = box.split(factor=0.5, align=True)
            x.prop(self.sd, "subseed", text="")
            x.prop(self.sd, "subseed_strength")
            x = box.split(factor=0.5, align=True)
            x.prop(self.sd, "seed_resize_from_w")
            x.prop(self.sd, "seed_resize_from_h")
        layout.separator()
        layout.label(text="ControlNet:")

        r = layout.row()
        r.template_list(
            ControlNetPassList.bl_idname,
            "",
            self,
            "control_net_passes",
            self,
            "active_control_net_pass_index"
        )
        l = r.column(align=True)
        l.operator(ControlNetPassAdd.bl_idname, icon="ADD", text="")
        l.operator(ControlNetPassRemove.bl_idname, icon="REMOVE", text="")
        l.separator()
        l.operator(ControlNetPassMoveUp.bl_idname, icon="TRIA_UP", text="")
        l.operator(ControlNetPassMoveDown.bl_idname, icon="TRIA_DOWN", text="")

        # check if the active index is valid
        if ControlNetPassRemove.poll(context):
            control_net = self.control_net_passes[self.active_control_net_pass_index]

            x = layout.split(align=True)
            x.prop(control_net, "srgb")
            x.prop(control_net, "use_mask")
            x.prop(control_net, "lowvram")

            col = layout.column(align=True)

            def split_prop(o, p, t):  # to align preprocessor settings
                x = col.split(factor=0.25, align=True)
                x.label(text=f"{t}:")
                x.prop(o, p, text="")

            split_prop(control_net, "model", "Model")
            split_prop(control_net, "control_mode", "Control Mode")
            split_prop(control_net, "resize_mode", "Resize Mode")
            split_prop(control_net, "module", "Preprocessor")

            if control_net.module != "none":
                x = col.split(factor=0.25, align=True)
                x.column()
                box = x.box().column(align=True)
                r = box.row(align=True)
                r.prop(control_net, "pixel_perfect")
                if not control_net.pixel_perfect:
                    r.prop(control_net, "processor_res")
                x = box.split(factor=0.5, align=True)
                x.prop(control_net, "threshold_a")
                x.prop(control_net, "threshold_b")

            r = layout.column(align=True)
            r.prop(control_net, "weight")
            x = r.split(factor=0.5, align=True)
            x.prop(control_net, "guidance_start")
            x.prop(control_net, "guidance_end")

        layout.separator()
        r = layout.row()
        r.label(text="Tiled VAE:")
        r.prop(self.tiled_vae, "enabled")
        if self.tiled_vae.enabled:
            box = layout.box().column()
            c = box.column(align=True)
            x = c.split(align=True)
            x.prop(self.tiled_vae, "decoder_tile_size")
            x.prop(self.tiled_vae, "encoder_tile_size")
            c = box.split()
            c.prop(self.tiled_vae, "fast_decoder")
            c.prop(self.tiled_vae, "fast_encoder")
            c = box.split()
            c.prop(self.tiled_vae, "vae_to_gpu")
            if self.tiled_vae.fast_encoder:
                c.prop(self.tiled_vae, "color_fix")

    def draw_buttons(self, context, layout):
        if self.progress >= 0:
            layout.enabled = False
            layout.prop(self, "progress", slider=True)
        else:
            SendToSD.ui(self, layout)

    def init_node_tree(self, **k):
        inputs = []
        if self.ty == "IMAGE":
            inputs.append(('NodeSocketColor', "Scene Color"))
        inputs.extend(
            ('NodeSocketColor', f"ControlNet-{i}-{x.model}")
            for i, x in enumerate(self.control_net_passes)
        )
        super().init_node_tree(
            inputs=inputs,
            outputs=[],
            **k,
        )
        self.width = 256


class SendToSD(utils.NodeOperator):
    bl_idname = "sd.send_to_sd"
    bl_label = "Generate"

    def modal(self, context, event):
        context.area.tag_redraw()

        def save_results():
            self.node.progress = -1
            context.window_manager.event_timer_remove(self.timer)
            self.task.join()
            resp = self.resp
            if resp.status_code == 200:
                info = json.loads(resp.json()["info"])
                for i, data in enumerate(resp.json()["images"]):
                    data = base64.b64decode(data.split(",", 1)[0])
                    with tempfile.TemporaryDirectory() as dir:
                        path = os.path.join(dir, str(i))
                        with io.open(path, mode="w+b") as f:
                            f.write(data)

                        name = f"SDOutput_{i}"
                        if image := bpy.data.images.get(name):
                            image.unpack(method="REMOVE")
                            image.filepath = path
                        else:
                            image = bpy.data.images.load(path)
                            image.name = name

                        if image.depth != 32:  # convert results to rgba8
                            old_image = image
                            old_image.name += "__tmp"
                            image = bpy.data.images.new(
                                name=name,
                                width=image.size[0],
                                height=image.size[1],
                                alpha=True,
                                float_buffer=False,
                            )

                            # with numpy this is faster
                            image.pixels = numpy.array(old_image.pixels)

                            old_image.user_remap(image)
                            bpy.data.images.remove(old_image)

                        if i < len(info["infotexts"]):
                            sd_info = {
                                "text": info["infotexts"][i],
                                "prompt": info["all_prompts"][i],
                                "negative_prompt": info["all_negative_prompts"][i],
                                "seed": str(info["all_seeds"][i]),
                                "subseed": str(info["all_subseeds"][i]),

                                "batch_size": info["batch_size"],
                                "cfg_scale": info["cfg_scale"],
                                "clip_skip": info["clip_skip"],
                                "denoising_strength": info["denoising_strength"],
                                "width": info["width"],
                                "height": info["height"],
                                "sampler_name": info["sampler_name"],
                                "sd_model_hash": info["sd_model_hash"],
                            }

                            image["sd_info"] = sd_info

                        image.pack()

                for image in [
                    x for x in bpy.data.images
                    if re.match(r"^SDOutput_[0-9]*$", x.name) and int(x.name.split("_")[-1]) > i
                ]:
                    bpy.data.images.remove(image)

            else:
                raise Exception(resp.json())

        if event.type == 'ESC':
            api.post("/sdapi/v1/interrupt")
            save_results()
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if not self.task.is_alive():
                save_results()
                return {'FINISHED'}
            else:
                resp = api.get("/sdapi/v1/progress").json()
                self.node.progress = int(resp["progress"] * 100)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.node:
            return {"CANCELLED"}
        node: CompositorNodeSend = self.node
        with tempfile.TemporaryDirectory() as out_dir:
            node.node_tree.nodes.clear()

            input = node.node_tree.nodes.new("NodeGroupInput")

            dump = node.node_tree.nodes.new("CompositorNodeOutputFile")
            dump.base_path = out_dir
            dump.format.color_depth = "16"
            dump.format.color_mode = "RGB"
            dump.format.color_management = "OVERRIDE"
            dump.format.display_settings.display_device = "None"
            dump.format.view_settings.view_transform = "Standard"
            dump.inputs.clear()

            def to_output(i, t):
                with context.temp_override(node=dump):
                    bpy.ops.node.output_file_add_socket(file_path=f"{t}@")
                node.node_tree.links.new(i, dump.inputs[-1])

            def to_srgb(i):
                cs = node.node_tree.nodes.new(
                    "CompositorNodeConvertColorSpace"
                )
                cs.to_color_space = "sRGB"
                if i:
                    node.node_tree.links.new(i, cs.inputs[0])
                return cs.outputs[0]

            def to_mask(i):
                sep = node.node_tree.nodes.new(
                    "CompositorNodeSeparateColor"
                )
                inv = node.node_tree.nodes.new("CompositorNodeInvert")
                node.node_tree.links.new(i, sep.inputs[0])
                node.node_tree.links.new(sep.outputs[-1], inv.inputs[-1])
                return inv.outputs[0]

            idx = 0

            if node.ty == "IMAGE":
                srgb = to_srgb(input.outputs[idx])
                to_output(srgb, "Scene Color")
                if node.img2img.use_inpaint:
                    mask = to_mask(input.outputs[idx])
                    to_output(mask, "Scene Color-M")
                idx += 1

            for i, x in enumerate(node.control_net_passes):
                name = f"ControlNet-{i}-{x.model}"
                if x.srgb:
                    img = to_srgb(input.outputs[idx])
                else:
                    img = input.outputs[idx]
                to_output(img, name)
                if x.use_mask:
                    mask = to_mask(input.outputs[idx])
                    to_output(mask, f"{name}-M")
                idx += 1

            def render_all_openpose(tree):
                for node in tree.nodes:
                    if node.bl_idname == nodes_pose.CompositorNodeOpenPose.bl_idname:
                        node.render(bpy.context)
                    if hasattr(node, "node_tree"):
                        render_all_openpose(node.node_tree)
            render_all_openpose(context.scene.node_tree)

            bpy.ops.render.render()

            node.node_tree.nodes.clear()

            inputs = {x.split("@")[0]: x for x in os.listdir(out_dir)}

            sd: SDProperty = node.sd
            req = {
                "denoising_strength": sd.denoising_strength,
                "prompt": sd.prompt,
                "seed": sd.seed,
                "sampler_name": sd.sampler_name,
                "batch_size": sd.batch_size,
                "n_iter": sd.n_iter,
                "steps": sd.steps,
                "cfg_scale": sd.cfg_scale,
                "width": sd.width,
                "height": sd.height,
                "negative_prompt": sd.negative_prompt,
                "alwayson_scripts": {}
            }
            if sd.seed_extras:
                req.update({
                    "subseed": sd.subseed,
                    "subseed_strength": sd.subseed_strength,
                    "seed_resize_from_h": sd.seed_resize_from_h,
                    "seed_resize_from_w": sd.seed_resize_from_w,
                })
            cnet_list: list[ControlNetPassProperty] = node.control_net_passes
            if cnet_list:
                cnet_req_list = []
                for i, cnet in enumerate(cnet_list):
                    name = f"ControlNet-{i}-{cnet.model}"
                    p = os.path.join(
                        out_dir,
                        inputs[name],
                    )
                    cnet_req = {
                        "input_image": base64.b64encode(
                            open(p, 'rb').read()
                        ).decode('utf-8'),
                        "model": cnet.model,
                        "module": "none",
                        "weight": cnet.weight,
                        "resize_mode": int(cnet.resize_mode),
                        "control_mode": int(cnet.control_mode),
                        "lowvram": cnet.lowvram,
                        "guidance_start": cnet.guidance_start,
                        "guidance_end": cnet.guidance_end,
                    }
                    if cnet.use_mask:
                        cnet_req.update({
                            "mask": base64.b64encode(
                                open(os.path.join(
                                    out_dir,
                                    inputs[f"{name}-M"],
                                ), 'rb').read()
                            ).decode('utf-8'),
                        })
                    if cnet.module != "none":
                        cnet_req.update({
                            "module": cnet.module,
                            "pixel_perfect": cnet.pixel_perfect,
                            "processor_res": cnet.processor_res,
                            "threshold_a": cnet.threshold_a,
                            "threshold_b": cnet.threshold_b,
                        })
                    cnet_req_list.append(cnet_req)

                req["alwayson_scripts"].update({
                    "controlnet": {
                        "args": cnet_req_list
                    }
                })
            if node.tiled_vae.enabled:
                req["alwayson_scripts"].update({
                    "Tiled VAE": {
                        "args": [
                            True,
                            node.tiled_vae.encoder_tile_size,
                            node.tiled_vae.decoder_tile_size,
                            node.tiled_vae.vae_to_gpu,
                            node.tiled_vae.fast_decoder,
                            node.tiled_vae.fast_encoder,
                            node.tiled_vae.color_fix,
                        ],
                    },
                })
            if node.ty == "IMAGE":
                img2img: SDIMG2IMGProperty = node.img2img
                req.update({
                    "init_images": [
                        base64.b64encode(
                            open(os.path.join(
                                out_dir,
                                inputs[f"Scene Color"],
                            ), 'rb').read()
                        ).decode('utf-8')
                    ],
                    "resize_mode": int(img2img.resize_mode),
                })
                if img2img.use_inpaint:
                    req.update({
                        "mask": base64.b64encode(
                            open(os.path.join(
                                out_dir,
                                inputs[f"Scene Color-M"],
                            ), 'rb').read()
                        ).decode('utf-8'),
                        "mask_blur": img2img.mask_blur,
                        "inpainting_fill": int(img2img.inpainting_fill),
                        "inpaint_full_res": img2img.inpaint_full_res,
                    })
                    if img2img.inpaint_full_res:
                        req.update({
                            "inpaint_full_res_padding": img2img.inpaint_full_res_padding,
                        })
                url = "/sdapi/v1/img2img"
            else:
                txt2img: SDTXT2IMGProperty = node.txt2img
                if txt2img.enable_hr:
                    req.update({
                        "enable_hr": txt2img.enable_hr,
                        "hr_scale": txt2img.hr_scale,
                        "hr_resize_x": txt2img.hr_resize_x,
                        "hr_resize_y": txt2img.hr_resize_y,
                        "hr_upscaler": txt2img.hr_upscaler,
                        "hr_second_pass_steps": txt2img.hr_second_pass_steps,
                    })
                url = "/sdapi/v1/txt2img"

            def task(self):
                self.resp = api.post(url, json=req)

            self.task = threading.Thread(target=task, args=(self,))
            self.task.start()
            self.timer = context.window_manager.event_timer_add(
                0.5,
                window=context.window,
            )
            context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


classes = [
    SDProperty, SDIMG2IMGProperty, SDTXT2IMGProperty,
    ControlNetPassProperty, TiledVAEProperty,
    ControlNetPassList,
    ControlNetPassAdd, ControlNetPassRemove,
    ControlNetPassMoveUp, ControlNetPassMoveDown,
    CompositorNodeSend, SendToSD
]


nodes = [
    ("COMPOSITOR", CompositorNodeSend)
]
