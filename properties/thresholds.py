import numpy as np
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


def _on_toggle_visibility(self, context):
    if self.is_visible:
        bpy.ops.auto_remesher.draw_selected_layer(selected_layer_id=self.layer_id)
    else:
        bpy.ops.auto_remesher.clear_selected_layer(selected_layer_id=self.layer_id)
        

class AutoRemesherLayerItem(bpy.types.PropertyGroup):
    layer_id: bpy.props.IntProperty(name="Layer", default=0, min=0, max=255, description="Layer number (0 = largest angle, higher = smaller angle)")
    color_attr_name: bpy.props.StringProperty(
        name="Color Attribute Name",
        description="Name of the color attribute for this layer",
        default="all_crease_color"
    )
    color: bpy.props.FloatVectorProperty(
        name="color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0)
    )
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=True, 
                                       description="Whether this layer is currently visible in the visualiser or not", 
                                       update=_on_toggle_visibility)
    
    def get_buffer(self, context):
        attr_name = self.color_attr_name
        mesh = context.scene.auto_remesher.remesher.mesh.data
        
        color_attrs = getattr(mesh, "color_attributes", None)
        color_attr = color_attrs.get(attr_name)
        num_face_corners = len(color_attr.data)
        buf = np.zeros(num_face_corners * 4, dtype=np.float16)
        
        color_attr.data.foreach_get('color', buf)
        return buf