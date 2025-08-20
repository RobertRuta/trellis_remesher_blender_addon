from trellis_remesher_blender_addon.properties.thresholds import AutoRemesherLayerItem
from ..utils import props_accesor as p, mesh_attribute_accessor as mesh_attr

import bpy
import numpy as np
import fnmatch


class AUTO_REMESHER_OT_vp_crease_visualiser(bpy.types.Operator):
    bl_idname = "auto_remesher.vp_crease_vis"
    bl_label = "Apply VP Crease Visualiser"
    bl_description = "Apply vertex paint visualization of crease edges using face corner colors"

    def execute(self, context):
        
        try:
            mesh_obj = p.get_mesh(context)
            mesh = mesh_obj.data       
            
            p.build_crease_layers_from_thresholds(context)
            crease_layers = p.get_crease_layers(context)
            
            # Ensure we're in object mode for mesh operations
            was_edit = mesh_obj.mode == 'EDIT'
            if was_edit:
                bpy.ops.object.mode_set(mode='OBJECT')

            face_corner_layers = mesh_attr.extract_corner_layer_ids(mesh)
            
            # Init/Reset face corner color attributes used for painting
            for layer_id in range(-2, len(crease_layers)):
                mesh_attr.get_corner_color_layer(mesh, layer_id, create=True)

            # Array of colors fo each layer
            layer_colors = np.array(
                [[float(t.color[0]), float(t.color[1]), float(t.color[2]), 1.0] for t in crease_layers],
                dtype=np.float32
            ).clip(0.0, 1.0)

            ######### Paint the face corners #########
            # Cumulative mask of colored face corners
            mask = np.zeros(len(face_corner_layers), dtype=bool)
            # should_accumulate = rprops.accumulate_lower_layers
            should_accumulate = False
            combined_layer_colors = np.ones((len(face_corner_layers), 4), dtype=np.float32)
            
            for layer_id in range(len(crease_layers)):
                current_layer_mask = (face_corner_layers == layer_id)
                mask = mask | current_layer_mask if should_accumulate else current_layer_mask    
                mesh_attr.set_corner_layer_color(mesh, layer_id, rgba=layer_colors[layer_id])
                
                combined_layer_colors[current_layer_mask] = layer_colors[layer_id]
            
            # Set face corner color data for combined color layer
            mesh_attr.set_corner_layer_color(mesh, -1, data=combined_layer_colors.ravel())
            mesh_attr.display_chosen_layer(mesh, -1)
            
            _set_active_color_attr(self, mesh, )
            
            mesh.update()    
            if was_edit:
                bpy.ops.object.mode_set(mode='EDIT')
            
            self.report({'INFO'}, "Successfully created attributes.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Vertex paint visualization failed: {e}")
            return {'CANCELLED'}


class AUTO_REMESHER_OT_clear_vp_visualisation(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_vp_vis"
    bl_label = "Clear VP Visualisation"
    bl_description = "Delete all vertex paint visualization attributes ending with '_crease_color'"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        
        rprops.crease_layers.clear()  # Clear all crease layers
        rprops.crease_layers_index = 0
        
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data
        
        removed = 0

        # Gather matching attributes first (avoid modifying while iterating)
        attrs_to_remove = [
            attr.name for attr in mesh.attributes
            if fnmatch.fnmatch(attr.name, "*_crease_color")
        ]

        for name in attrs_to_remove:
            mesh.attributes.remove(mesh.attributes[name])
            removed += 1

        if removed > 0:
            mesh.update()
            self.report({'INFO'}, f"Removed {removed} crease color attribute(s).")
        else:
            self.report({'INFO'}, "No crease color attributes found.")

        return {'FINISHED'}


class AUTO_REMESHER_OT_draw_selected_layer(bpy.types.Operator):
    bl_idname = "auto_remesher.draw_selected_layer"
    bl_label = "Draw Selected Layer"
    
    selected_layer_id: bpy.props.IntProperty(default=-1)
    
    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        
        layer_id = self.selected_layer_id
        layer = rprops.crease_layers[layer_id]
        
        mesh = rprops.mesh.data
        color_data = layer.get_buffer(context)
        layer_mask = color_data < 1
        display_attr = _get_corner_color_attr(mesh, "display_crease_color")
        display_data = _get_attr_color_data(display_attr)
        new_data = np.where(layer_mask, color_data, display_data)
        _validate_and_set_corner_color_attr(self, mesh, "display_crease_color", new_data)
        return {'FINISHED'}
        
        
class AUTO_REMESHER_OT_clear_selected_layer(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_selected_layer"
    bl_label = "Clear Selected Layer"
    
    selected_layer_id: bpy.props.IntProperty(default=-1)
    
    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        
        layer_id = self.selected_layer_id
        layer = rprops.crease_layers[layer_id]
        
        mesh = rprops.mesh.data
        try:
            color_data = layer.get_buffer(context)
            color_mask = color_data < 1
            display_attr = _get_corner_color_attr(mesh, "display_crease_color")
            data = _get_attr_color_data(display_attr)
            new_data = np.where(color_mask, 1.0, data)
            _validate_and_set_corner_color_attr(self, mesh, "display_crease_color", new_data)
            self.report({'INFO'}, f"Successfully cleared layer {self.selected_layer_id}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear layer {self.selected_layer_id}: {e}")
        return {'FINISHED'}
        
# Helper functions
def _validate_and_set_corner_color_attr(self, mesh, name: str, data=None):
    attribute = mesh.attributes.get(name)
    if attribute is None:
        attribute = mesh.attributes.new(name=name, type='BYTE_COLOR', domain='CORNER')
    elif attribute.domain != 'CORNER' or attribute.data_type != 'BYTE_COLOR':
        mesh.attributes.remove(attribute)
        attribute = mesh.attributes.new(name=name, type='BYTE_COLOR', domain='CORNER')
    # Initialize with white color
    if data is not None:
        attribute.data.foreach_set("color", data)
    else:
        # Set to white by default
        attribute.data.foreach_set("color", [1.0] * (len(attribute.data)*4))


def _get_corner_color_attr(mesh, name: str):
    color_attributes = getattr(mesh, "color_attributes", None)
    if color_attributes is None:
        return None
    return color_attributes.get(name)


def _get_attr_color_data(attr):
    if attr is None:
        return None
    buf = np.ones(len(attr.data)*4, np.float16)
    attr.data.foreach_get('color', buf)
    return buf

        
# Helper function
def _set_active_color_attr(self, mesh):
    color_attributes = getattr(mesh, "color_attributes", None)
    if color_attributes is None:
        self.report({'WARNING'}, "No color attributes found in mesh.")
        display_attr = mesh.attributes.get("display_crease_color")
        mesh.attributes.active_color = display_attr
        return
    
    display_attribute = color_attributes.get("display_crease_color")
    if display_attribute is None:
        self.report({'WARNING'}, "Display crease color attribute not found. No active color attribute set.")
        return
    color_attributes.active_color = display_attribute