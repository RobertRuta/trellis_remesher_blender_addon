import bpy

class AutoRemesherProperties(bpy.types.PropertyGroup):
    __blender_context_target__ = ("Scene", "auto_remesher")
    
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