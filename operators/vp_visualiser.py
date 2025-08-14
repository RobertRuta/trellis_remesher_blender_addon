import bpy
import numpy as np

class AUTO_REMESHER_OT_vp_crease_visualiser(bpy.types.Operator):
    bl_idname = "auto_remesher.vp_crease_vis"
    bl_label = "Apply VP Crease Visualiser"
    bl_description = "Apply vertex paint visualization of crease edges using face corner colors"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        thresholds = [rprops.single_threshold] if rprops.is_single_threshold else rprops.multi_thresholds
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        if len(thresholds) == 0:
            self.report({'ERROR'}, "No thresholds found.")
            return {'CANCELLED'}

        mesh = obj.data
        try:
            # Ensure we're in object mode for mesh operations
            was_edit = obj.mode == 'EDIT'
            if was_edit:
                bpy.ops.object.mode_set(mode='OBJECT')

            # Helper function
            def get_corner_color_attr(name: str):
                attr = mesh.attributes.get(name)
                if attr is None:
                    attr = mesh.attributes.new(name=name, type='BYTE_COLOR', domain='CORNER')
                elif attr.domain != 'CORNER' or attr.data_type != 'BYTE_COLOR':
                    mesh.attributes.remove(attr)
                    attr = mesh.attributes.new(name=name, type='BYTE_COLOR', domain='CORNER')
                return attr

            # Get edge crease layer attribute
            crease_layer_attr = mesh.attributes.get('crease_layer')
            if crease_layer_attr is None:
                self.report({'ERROR'}, "No crease layer data found. Run crease detection first.")
                return {'CANCELLED'}

            # Array of edge crease layer ids
            n_edges = len(mesh.edges)
            edge_crease_layers = np.empty(n_edges, dtype=np.int32)
            try:
                crease_layer_attr.data.foreach_get("value", edge_crease_layers)
            except Exception:
                self.report({'ERROR'}, "Bug! Failed to get crease layer data.")
                return {'CANCELLED'}

            # Perpare array of edge indices for each face corner to be colored
            num_face_corners = len(mesh.loops)
            face_corner_edge_ids = np.empty(num_face_corners, dtype=np.int32)
            mesh.loops.foreach_get("edge_index", face_corner_edge_ids)

            # Set crease layer ids for each face corner
            face_corner_layers = edge_crease_layers[face_corner_edge_ids]  # shape (n_loops,)
            face_corner_crease_mask = (face_corner_layers >= 0)

            # Get/Init face corner color attributes
            get_corner_color_attr("display_crease_color")
            all_color_attr = get_corner_color_attr("all_crease_color")

            # Get attributes fo each color layer
            layer_color_attrs = []
            for i, _ in enumerate(thresholds):
                layer_color_attr = get_corner_color_attr(f"L{i}_crease_color")
                layer_color_attrs.append(layer_color_attr)

            # Reset/Init all attributes to white
            white_face_corners = np.ones((num_face_corners, 4), dtype=np.float32)
            all_color_attr.data.foreach_set("color", white_face_corners.ravel())
            for layer_color_attr in layer_color_attrs:
                layer_color_attr.data.foreach_set("color", white_face_corners.ravel())

            # Array of colors fo each layer
            layer_colors = np.array(
                [[float(t.color[0]), float(t.color[1]), float(t.color[2]), 1.0] for t in thresholds],
                dtype=np.float32
            ).clip(0.0, 1.0)

            ######### Paint the face corners #########
        
            # Cumulative mask of colored face corners
            mask = np.zeros(num_face_corners, dtype=bool)
            should_accumulate = rprops.accumulate_lower_layers
            combined_layer_colors = white_face_corners.copy()
            
            for layer_id in range(len(thresholds)):
                current_layer_mask = face_corner_crease_mask & (face_corner_layers == layer_id)
                mask = mask | current_layer_mask if should_accumulate else current_layer_mask    
                # Color masked face corners with current layer color
                face_corner_colors = white_face_corners.copy()
                face_corner_colors[mask] = layer_colors[layer_id]
                # Set face corner color data for current layer
                layer_color_attrs[layer_id].data.foreach_set("color", face_corner_colors.ravel())
                combined_layer_colors[current_layer_mask] = layer_colors[layer_id]
            
            # Set face corner color data for combined color layer
            all_color_attr.data.foreach_set("color", combined_layer_colors.ravel())

            mesh.update()            
            if was_edit:
                bpy.ops.object.mode_set(mode='EDIT')
            
            # Switch to the active crease layer
            bpy.ops.auto_remesher.switch_crease_display(display_layer_index=rprops.active_crease_layer_display)
            
            self.report({'INFO'}, "Successfully created attributes.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Vertex paint visualization failed: {e}")
            return {'CANCELLED'}


class AUTO_REMESHER_OT_clear_vp_visualisation(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_vp_vis"
    bl_label = "Clear VP Visualisation"
    bl_description = "Clear vertex paint visualization colors"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data
        attr_name = "display_crease_color"
        attr = mesh.attributes.get(attr_name)
        
        if attr is not None:
            # Reset all colors to white
            default_color = (255, 255, 255, 255)
            for i in range(len(attr.data)):
                attr.data[i].color = default_color
            
            mesh.update()
            self.report({'INFO'}, "Vertex paint visualization cleared.")
        else:
            self.report({'INFO'}, "No vertex paint visualization found.")

        return {'FINISHED'}


class AUTO_REMESHER_OT_switch_crease_display(bpy.types.Operator):
    bl_idname = "auto_remesher.switch_crease_display"
    bl_label = "Switch Crease Display"
    bl_description = "Switch the visible crease_color attribute between All and a specific layer"

    display_layer_index: bpy.props.IntProperty(default=-1, min=-1)

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data

        # Helper function
        def get_attr(name: str):
            attr = mesh.attributes.get(name)
            if attr is None:
                self.report({'ERROR'}, f"Attribute '{name}' not found. Run visualiser first.")
                return None
            return attr

        # Get attributes from mesh
        display_attr = get_attr("display_crease_color")
        selected_attr = get_attr("all_crease_color") if self.display_layer_index == -1 else get_attr(f"L{self.display_layer_index}_crease_color")
        if selected_attr is None or display_attr is None:
            return {'CANCELLED'}

        if len(selected_attr.data) != len(display_attr.data):
            self.report({'ERROR'}, "Bug! Mismatched attribute lengths.")
            return {'CANCELLED'}

        try:
            num_corners = len(selected_attr.data)
            color_buffer = [0.0] * (num_corners * 4)
            # Update the display attribute with the selected one   
            selected_attr.data.foreach_get("color", color_buffer)
            display_attr.data.foreach_set("color", color_buffer)
        except Exception:
            self.report({'WARNING'}, "Bug! Failed to copy crease colors efficiently.")
            for i in range(len(selected_attr.data)):
                display_attr.data[i].color = selected_attr.data[i].color

        rprops.active_crease_layer_display = self.display_layer_index
        return {'FINISHED'}
