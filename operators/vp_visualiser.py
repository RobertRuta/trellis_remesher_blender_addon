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
            
            crease_layers = p.get_crease_layers(context)
            
            # Ensure we're in object mode for mesh operations
            was_edit = mesh_obj.mode == 'EDIT'
            if was_edit:
                bpy.ops.object.mode_set(mode='OBJECT')

            face_corner_layers = mesh_attr.extract_corner_layer_ids(mesh)
            
            # Init/Reset face corner color attributes used for painting
            for layer_id in range(-2, len(crease_layers)):
                mesh_attr.get_corner_color_layer(mesh, layer_id, create=True)

            ######### Paint the face corners #########
            # Cumulative mask of colored face corners
            mask = np.zeros(len(face_corner_layers), dtype=bool)
            # should_accumulate = rprops.accumulate_lower_layers
            should_accumulate = False
            combined_layer_colors = np.ones((len(face_corner_layers), 4), dtype=np.float32)
            
            for layer in crease_layers:
                current_layer_mask = (face_corner_layers == layer.layer_id)
                mask = mask | current_layer_mask if should_accumulate else current_layer_mask    
                if layer.is_visible:
                    mesh_attr.set_corner_layer_color(mesh, layer.layer_id, rgba=layer.color)
                    combined_layer_colors[current_layer_mask] = layer.color
            
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
        try:
            rprops = p.get_rprops(context)
            mesh = p.get_mesh(context).data
            # Clear created attributes attached to mesh
            removed = mesh_attr.delete_created_attributes(mesh, domain='CORNER')
            crease_layers_prop = p.get_crease_layers(context)
            crease_layers_prop.clear()
            rprops.crease_layers_index = 0
        except Exception as e:
            self.report({'ERROR'}, e)
            return {'CANCELLED'}
        
        if len(removed) < 1:
            self.report({'WARNING'}, f"Removed {len(removed)} attributes. Should be greater than 0.")
        else:
            self.report({'INFO'}, f"Removed {len(removed)} attributes and reset relevant props.")
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
        try:
            mesh_attr.set_corner_layer_color(mesh, layer_id, rgba=layer.color)
            mesh_attr.display_update_layer(mesh, layer_id)
        except:
            self.report({'ERROR'}, f"Failed to draw specified layer: {layer.color_attr_name}")
            return {'CANCELLED'}
        
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
            # No data provided -> reset to white
            mesh_attr.set_corner_layer_color(mesh, layer_id)
            mesh_attr.display_update_layer(mesh, layer_id)
            self.report({'INFO'}, f"Successfully cleared layer {self.selected_layer_id}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear layer {self.selected_layer_id}: {e}")
        return {'FINISHED'}
        
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