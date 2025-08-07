import bpy
import urllib.parse


def update_prompt_mode(self, context):
    # Prevent recursive loop by only changing if necessary
    if self.use_text_prompt and self.use_image_prompt:
        self.use_image_prompt = False
    elif self.use_image_prompt and self.use_text_prompt:
        self.use_text_prompt = False


def update_api(self, context):
    self.api_url = f"http://{self.server_host}:{self.server_port}"


# def update_host_and_port(self, context):
#     parsed = urllib.parse.urlparse(self.api_url)
#     if parsed.scheme in {"http", "https"} and parsed.hostname and parsed.port:
#         self.server_host = parsed.hostname
#         self.server_port = parsed.port


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