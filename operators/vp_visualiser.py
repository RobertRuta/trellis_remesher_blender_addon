import bpy
import bmesh
import math


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

            # Create or get the face corner color attribute
            color_attr_name = "crease_color"
            color_attr = mesh.attributes.get(color_attr_name)
            if color_attr is None:
                color_attr = mesh.attributes.new(name=color_attr_name, type='BYTE_COLOR', domain='CORNER')
            elif color_attr.domain != 'CORNER' or color_attr.data_type != 'BYTE_COLOR':
                # Remove existing attribute if it's wrong type
                mesh.attributes.remove(color_attr)
                color_attr = mesh.attributes.new(name=color_attr_name, type='BYTE_COLOR', domain='CORNER')

            # Get crease data from edge domain
            crease_attr = mesh.attributes.get('crease_layer')
            if crease_attr is None:
                self.report({'ERROR'}, "No crease layer data found. Run crease detection first.")
                return {'CANCELLED'}

            # Create bmesh for processing
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

            # Read crease layer values directly from mesh edge attribute by index
            edge_layers = []
            try:
                # Fast path
                edge_layers = [0] * len(mesh.edges)
                crease_attr.data.foreach_get("value", edge_layers)
            except Exception:
                # Fallback path
                edge_layers = [int(d.value) for d in crease_attr.data]

            # Initialize all face corners to default color (white)
            default_color = (1.0, 1.0, 1.0, 1.0)  # RGBA in 0..1

            def paint_edge(edge, col):
                for face in edge.link_faces:
                    for vert in edge.verts:
                        for loop in face.loops:
                            if loop.vert == vert:
                                color_attr.data[loop.index].color = col

            # Paint edges based on threshold layer
            for edge in bm.edges:
                edge_layer = edge_layers[edge.index]
                if edge_layer == -1:
                    color = default_color
                else:
                    color = thresholds[edge_layer].color
                paint_edge(edge, color)

            bm.free()

            # Update the mesh
            mesh.update()

            # Return to edit mode if we were there
            if was_edit:
                bpy.ops.object.mode_set(mode='EDIT')

            self.report({'INFO'}, "VP visualization applied with layer-based coloring.")
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
        attr_name = "crease_color"
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
