import bpy


class CopyText(bpy.types.Operator):
    bl_idname = f"sd.copy_text"
    bl_label = "Copy Text"

    text: bpy.props.StringProperty()

    def execute(self, context):
        context.window_manager.clipboard = self.text
        return {'FINISHED'}


class ImagePanel(bpy.types.Panel):
    bl_idname = "IMAGE_PT_sd_image"
    bl_label = "Stable Diffusion"
    bl_space_type = 'IMAGE_EDITOR'
    bl_category = "Image"
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout.column()
        info = context.edit_image["sd_info"]

        def prop(k, v, copy=False):
            s = layout.split(factor=0.333)
            col = s.column()
            col.alignment = 'RIGHT'
            col.label(text=str(k))
            r = s.row()
            r.label(text=str(v))
            if copy:
                col = r.column()
                col.operator(
                    CopyText.bl_idname, text="", icon="COPYDOWN"
                ).text = v

        prop("Seed", info['seed'], True)
        prop("Subseed", info['subseed'], True)
        prop("Size", f"{info['width']}x{info['height']}")
        prop("Batch Size", info['batch_size'])
        prop("Sampler", info['sampler_name'])
        prop("CFG Scale", info['cfg_scale'])
        prop("Denoising Strength", info['denoising_strength'])
        prop("Clip Skip", info['clip_skip'])
        prop("Model Hash", info['sd_model_hash'], True)

        layout.operator(
            CopyText.bl_idname, text="Copy Summary", icon="COPYDOWN"
        ).text = info['text']

    @ classmethod
    def poll(cls, context):
        return getattr(context.space_data, "image") and context.space_data.image.get("sd_info")


classes = [
    CopyText, ImagePanel,
]
