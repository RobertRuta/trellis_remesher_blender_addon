import bpy
import bmesh


class AUTO_REMESHER_OT_vp_crease_visualiser(bpy.types.Operator):
    bl_idname = "auto_remesher.vp_crease_vis"
    bl_label = "Apply VP Crease Visualiser"
    bl_description = "Apply vertex paint visualization of crease edges using face corner colors"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data
        try:
            # Ensure we're in object mode for mesh operations
            was_edit = obj.mode == 'EDIT'
            if was_edit:
                bpy.ops.object.mode_set(mode='OBJECT')

            # Create or get the face corner color attribute
            attr_name = "crease_color"
            attr = mesh.attributes.get(attr_name)
            if attr is None:
                attr = mesh.attributes.new(name=attr_name, type='BYTE_COLOR', domain='CORNER')
            elif attr.domain != 'CORNER' or attr.data_type != 'BYTE_COLOR':
                # Remove existing attribute if it's wrong type
                mesh.attributes.remove(attr)
                attr = mesh.attributes.new(name=attr_name, type='BYTE_COLOR', domain='CORNER')

            # Get crease data from edge domain
            crease_attr = mesh.attributes.get('crease_edge')
            if crease_attr is None:
                self.report({'ERROR'}, "No crease data found. Run crease detection first.")
                return {'CANCELLED'}

            # Create bmesh for processing
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

            # Get crease layer from bmesh
            crease_layer = bm.edges.layers.float.get('crease_edge')
            if crease_layer is None:
                self.report({'ERROR'}, "No crease data in bmesh. Run crease detection first.")
                bm.free()
                return {'CANCELLED'}

            # Initialize all face corners to default color (white)
            default_color = (255, 255, 255, 255)  # RGBA
            for poly in mesh.polygons:
                for loop_idx in poly.loop_indices:
                    attr.data[loop_idx].color = default_color

            # Color edges that meet crease threshold
            threshold = rprops.viz_threshold
            crease_color = (255, 0, 0, 255)  # Red for creases
            
            for edge in bm.edges:
                crease_value = edge[crease_layer]
                if crease_value >= threshold:
                    # Color all face corners of faces connected to this edge
                    for face in edge.link_faces:
                        for vert in edge.verts:
                            # Find the loop indices for this vertex in this face
                            for loop in face.loops:
                                if loop.vert == vert:
                                    # Get the mesh loop index
                                    mesh_loop_idx = loop.index
                                    attr.data[mesh_loop_idx].color = crease_color

            bm.free()

            # Update the mesh
            mesh.update()

            # Return to edit mode if we were there
            if was_edit:
                bpy.ops.object.mode_set(mode='EDIT')

            self.report({'INFO'}, f"Vertex paint visualization applied. Creases colored red.")
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
