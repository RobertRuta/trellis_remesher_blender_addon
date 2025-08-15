import bpy


class AutoRemesherThresholdItem(bpy.types.PropertyGroup):
    layer_id: bpy.props.IntProperty(name="Layer", default=0, min=0, max=255, description="Layer number (0 = largest angle, higher = smaller angle)")
    angle_deg: bpy.props.FloatProperty(name="Angle (°)", default=20.0, min=0.0, max=180.0)
    color: bpy.props.FloatVectorProperty(
        name="color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0)
    )


class AutoRemesherLayerItem(bpy.types.PropertyGroup):
    layer_id: bpy.props.IntProperty(name="Layer", default=0, min=0, max=255, description="Layer number (0 = largest angle, higher = smaller angle)")
    color: bpy.props.FloatVectorProperty(
        name="color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0)
    )
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=True, description="Whether this layer is currently visible in the visualiser or not")