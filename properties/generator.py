import bpy


def update_prompt_mode(self, context):
    # Prevent recursive loop by only changing if necessary
    if self.use_text_prompt and self.use_image_prompt:
        self.use_image_prompt = False
    elif self.use_image_prompt and self.use_text_prompt:
        self.use_text_prompt = False


def update_image_path(self, context):
    if self.image:
        # Convert to absolute file path
        self.image_path = bpy.path.abspath(self.image.filepath)
    else:
        self.image_path = ""


class AutoRemesherGeneratorProperties(bpy.types.PropertyGroup):
    """Generation prompt and quality settings."""

    generation_quality: bpy.props.EnumProperty(
        name="Generation Quality",
        description="Generation quality settings. Impact generation time and quality.",
        items=[
            ('LOW', "Low", "Fastest"),
            ('MID', "Mid", "Faster"),
            ('HIGH', "High", "Slow"),
        ],
        default='LOW'
    )

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

    image: bpy.props.PointerProperty(
        name="Image Prompt",
        description="Image we want to TRELLIS to use as a prompt",
        type=bpy.types.Image,
        update=update_image_path
    )

    image_path: bpy.props.StringProperty(
        name="Image Prompt",
        description="Image path to send to TRELLIS",
        default=""
    )
    
    # Internal properties for prompt mode management
    use_text_prompt: bpy.props.BoolProperty(default=True)
    use_image_prompt: bpy.props.BoolProperty(default=False)
