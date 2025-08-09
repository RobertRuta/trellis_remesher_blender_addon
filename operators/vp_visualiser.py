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

            # Read crease values directly from mesh edge attribute by index
            edge_values = []
            try:
                # Fast path
                edge_values = [0.0] * len(mesh.edges)
                crease_attr.data.foreach_get("value", edge_values)
            except Exception:
                # Fallback path
                edge_values = [float(d.value) for d in crease_attr.data]

            # Initialize all face corners to default color (white)
            default_color = (1.0, 1.0, 1.0, 1.0)  # RGBA in 0..1
            for poly in mesh.polygons:
                for loop_idx in poly.loop_indices:
                    attr.data[loop_idx].color = default_color

            # Color edges according to threshold list only (no base color)
            multi = getattr(rprops, "threshold_mode", 'MULTI') == 'MULTI'
            tol = 0.05

            def paint_edge(edge, col):
                for face in edge.link_faces:
                    for vert in edge.verts:
                        for loop in face.loops:
                            if loop.vert == vert:
                                attr.data[loop.index].color = col

            if multi:
                # Compute dihedral angles once (degrees) for categorisation
                bm.normal_update()
                edge_angle_deg = {}
                for edge in bm.edges:
                    if len(edge.link_faces) == 2:
                        f0, f1 = edge.link_faces
                        dot = max(-1.0, min(1.0, f0.normal.dot(f1.normal)))
                        edge_angle_deg[edge.index] = math.degrees(math.acos(dot))
                    else:
                        edge_angle_deg[edge.index] = 180.0  # treat boundary as very sharp

                # Paint in list order; for each threshold, color edges whose angle meets it
                thresholds_snapshot = list(rprops.thresholds)
                for item in thresholds_snapshot:
                    rgba = item.color
                    # item.color is already 0..1
                    col = (float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
                    min_angle = float(item.angle_deg)
                    for edge in bm.edges:
                        # Only visualize edges that were marked by detection (strength > 0)
                        if edge_values[edge.index] <= 0.0:
                            continue
                        if edge_angle_deg.get(edge.index, 0.0) + 1e-6 >= min_angle:
                            paint_edge(edge, col)
            else:
                # Single pass: color only edges that match any threshold strength; leave others white
                for edge in bm.edges:
                    v = edge_values[edge.index]
                    for item in rprops.thresholds:
                        if abs(v - float(item.strength)) <= tol:
                            rgba = item.color
                            col = (float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
                            paint_edge(edge, col)
                            break

            bm.free()

            # Update the mesh
            mesh.update()

            # Return to edit mode if we were there
            if was_edit:
                bpy.ops.object.mode_set(mode='EDIT')

            if multi:
                self.report({'INFO'}, "VP visualization applied with multi-threshold coloring.")
            else:
                self.report({'INFO'}, "VP visualization applied.")
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
