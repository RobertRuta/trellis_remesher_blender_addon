import bpy
from .server import AutoRemesherServerProperties
from .generator import AutoRemesherGeneratorProperties
from .remesher import AutoRemesherRemesherProperties


class AutoRemesherProperties(bpy.types.PropertyGroup):
    __blender_context_target__ = ("Scene", "auto_remesher")

    server: bpy.props.PointerProperty(type=AutoRemesherServerProperties)
    generator: bpy.props.PointerProperty(type=AutoRemesherGeneratorProperties)
    remesher: bpy.props.PointerProperty(type=AutoRemesherRemesherProperties)
