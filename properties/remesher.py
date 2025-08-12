import bpy
from .thresholds import AutoRemesherThresholdItem


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

    single_threshold_color: bpy.props.FloatVectorProperty(
        name="Crease Color",
        description="Color used for single-threshold visualization and as a base for generated sub-thresholds",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 0.3, 0.3, 1.0)
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

    # Dynamic threshold list
    single_threshold: bpy.props.PointerProperty(type=AutoRemesherThresholdItem)
    multi_thresholds: bpy.props.CollectionProperty(type=AutoRemesherThresholdItem)
    thresholds_index: bpy.props.IntProperty(name="Active Threshold", default=0)

    # Threshold mode: single or multi
    is_single_threshold: bpy.props.BoolProperty(
        name="Use Single Threshold",
        description="Enable to use a single angle, disable to use the dynamic thresholds list",
        default=True,  # False = Multi, True = Single
    )

    # Stats
    crease_count: bpy.props.IntProperty(
        name="Crease Count",
        description="Total number of edges currently marked as creases (crease_layer > 0)",
        default=0, min=0
    )
