import bpy


def update_prompt_mode(self, context):
    # Prevent recursive loop by only changing if necessary
    if self.use_text_prompt and self.use_image_prompt:
        self.use_image_prompt = False
    elif self.use_image_prompt and self.use_text_prompt:
        self.use_text_prompt = False


def update_api(self, context):
    self.api_url = f"http://{self.server_host}:{self.server_port}"


def update_image_path(self, context):
    if self.image:
        # Convert to absolute file path
        self.image_path = bpy.path.abspath(self.image.filepath)
    else:
        self.image_path = ""


class AutoRemesherProperties(bpy.types.PropertyGroup):
    __blender_context_target__ = ("Scene", "auto_remesher")
    
    server_host: bpy.props.StringProperty(
        name="Host",
        default="localhost",
        description="Server host (usually localhost)",
        update=update_api
    )

    server_port: bpy.props.IntProperty(
        name="Port",
        default=8765,
        description="Server port",
        update=update_api
    )

    advanced_server_config: bpy.props.BoolProperty(
        name="Advanced URL Config",
        default=False,
        description="Enable manual API URL configuration"
    )

    api_url: bpy.props.StringProperty(
        name="API URL",
        default="http://localhost:8765",
        description="Override full URL to the backend API",
    )

    connection_status: bpy.props.StringProperty(
        name="",
        default="Unknown",
        description="Connection check result"
    )
    
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

    mesh: bpy.props.PointerProperty(
        name="Loaded Mesh",
        description="Loaded or generated mesh",
        type=bpy.types.Object
    )