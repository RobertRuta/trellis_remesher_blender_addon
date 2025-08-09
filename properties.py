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


class AutoRemesherServerProperties(bpy.types.PropertyGroup):
    """Connection/server related settings."""

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


class AutoRemesherRemesherProperties(bpy.types.PropertyGroup):
    """Remesher target selection and detection settings."""

    mesh: bpy.props.PointerProperty(
        name="Loaded Mesh",
        description="Loaded or generated mesh",
        type=bpy.types.Object
    )

    crease_angle_threshold: bpy.props.FloatProperty(
        name="Angle Threshold (°)",
        description="Mark edges whose dihedral angle is greater than or equal to this value",
        default=30.0, min=0.0, max=180.0
    )

    crease_strength: bpy.props.FloatProperty(
        name="Crease Strength",
        description="Crease weight applied to detected edges (0.0 - 1.0)",
        default=1.0, min=0.0, max=1.0
    )

    mark_boundary_as_crease: bpy.props.BoolProperty(
        name="Treat Boundary as Crease",
        description="Mark open boundary edges as creases",
        default=True
    )

    clear_existing_creases: bpy.props.BoolProperty(
        name="Clear Existing First",
        description="Clear existing edge creases before detection",
        default=True
    )

    # Visualization settings
    show_crease_viz: bpy.props.BoolProperty(
        name="Show Crease Viz",
        description="Overlay crease edges using Geometry Nodes",
        default=False
    )

    viz_threshold: bpy.props.FloatProperty(
        name="Viz Threshold",
        description="Only visualize creases with value >= this threshold",
        default=0.5, min=0.0, max=1.0
    )

    viz_thickness: bpy.props.FloatProperty(
        name="Viz Thickness",
        description="Thickness of crease visualization (in Blender units)",
        default=0.01, min=0.0, soft_max=0.2
    )


class AutoRemesherProperties(bpy.types.PropertyGroup):
    __blender_context_target__ = ("Scene", "auto_remesher")

    server: bpy.props.PointerProperty(type=AutoRemesherServerProperties)
    generator: bpy.props.PointerProperty(type=AutoRemesherGeneratorProperties)
    remesher: bpy.props.PointerProperty(type=AutoRemesherRemesherProperties)