import bpy
from .thresholds import AutoRemesherThresholdItem, AutoRemesherLayerItem


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
        name="Crease color",
        description="color used for single-threshold visualization and as a base for generated sub-thresholds",
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
    
    # Re-run visualisation when visualisation logic changes
    def _update_vis(self, context):
        try:
            # Rebuild per-layer attributes according to the new mode
            bpy.ops.auto_remesher.vp_crease_vis()
        except Exception as e:
            print(f"Error updating visualisation: {e}")
            pass
        
    # Dynamic threshold list
    single_threshold: bpy.props.PointerProperty(type=AutoRemesherThresholdItem)
    multi_thresholds: bpy.props.CollectionProperty(type=AutoRemesherThresholdItem)
    thresholds_index: bpy.props.IntProperty(name="Active Threshold", default=0)
    num_thresholds : bpy.props.IntProperty(name="Threshold Count", default=0)
    crease_layers   : bpy.props.CollectionProperty(type=AutoRemesherLayerItem)
    crease_layers_index   : bpy.props.IntProperty(name="Active Layer", default=0)
    num_crease_layers : bpy.props.IntProperty(name="Crease Layer Count", default=0)

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
    
    # Currently selected crease layer to display
    active_crease_layer_display: bpy.props.IntProperty(
        name="Active Crease Layer Display",
        description="Currently displayed crease layer index (-1 = All)",
        default=-1, min=-1
    )

    # Whether to accumulate lower layers when viewing a specific layer
    accumulate_lower_layers: bpy.props.BoolProperty(
        name="Accumulate Lower Layers",
        description="When viewing a layer L, also show layers < L",
        default=False,
        update=_update_vis
    )
    
    def add_crease_layer(self, color_rgba, is_active):
        crease_layer = self.crease_layers.add()
        crease_layer.color = color_rgba
        crease_layer.is_active = is_active
        self.num_crease_layers += 1
        return crease_layer
    
    def add_crease_layer_from_threshold(self, threshold: AutoRemesherThresholdItem, is_active: bool = True, set_layer_id: bool = True):
        crease_layer = self.crease_layers.add()
        if set_layer_id:
            crease_layer.layer_id = threshold.layer_id
        crease_layer.color_attr_name = f"L{threshold.layer_id}_crease_color"
        crease_layer.color = threshold.color
        crease_layer.is_active = is_active
        self.num_crease_layers += 1
        return crease_layer

    def add_threshold(self, angle_deg: float, color_rgba):
        self.is_single_threshold = False
        threshold = self.multi_thresholds.add()
        threshold.angle_deg = angle_deg
        threshold.color = color_rgba
        self.num_thresholds += 1
        return threshold

    def sort_thresholds(self):
        """Reassign layer_id based on descending angle, without touching other values."""
        if self.is_single_threshold or len(self.multi_thresholds):
            pass
        # Sort thresholds by angle
        sorted_items = sorted(self.multi_thresholds, key=lambda t: t.angle_deg, reverse=True)
        # Update layer id
        for new_layer, t in enumerate(sorted_items):
            t.layer_id = new_layer