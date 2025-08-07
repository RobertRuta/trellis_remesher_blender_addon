import bpy


def update_prompt_mode(self, context):
    # Prevent recursive loop by only changing if necessary
    if self.use_text_prompt and self.use_image_prompt:
        self.use_image_prompt = False
    elif self.use_image_prompt and self.use_text_prompt:
        self.use_text_prompt = False


class AutoRemesherProperties(bpy.types.PropertyGroup):
    __blender_context_target__ = ("Scene", "auto_remesher")

    prompt_mode: bpy.props.EnumProperty(
        name="Prompt Mode",
        description="Choose between text or image prompt input",
        items=[
            ('TEXT', "Text", "Use a text prompt"),
            ('IMAGE', "Image", "Use an image prompt"),
        ],
        default='TEXT'
    )

    text_prompt: bpy.props.StringProperty(
        name="Text Prompt",
        description="Text prompt to send to TRELLIS",
        default=""
    )

    image_prompt: bpy.props.PointerProperty(
        name="Image Prompt",
        description="Image prompt to send to TRELLIS",
        type=bpy.types.Image
    )

    mesh: bpy.props.PointerProperty(
        name="Loaded Mesh",
        description="Loaded or generated mesh",
        type=bpy.types.Object
    )