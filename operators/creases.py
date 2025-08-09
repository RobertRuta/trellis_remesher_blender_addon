import math
import bpy
import bmesh


class AUTO_REMESHER_OT_detect_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.detect_creases"
    bl_label = "Detect Creases"
    bl_description = "Detect hard edges by dihedral angle and set edge creases"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data
        try:
            is_edit = (obj.mode == 'EDIT')
            if is_edit:
                bm = bmesh.from_edit_mesh(mesh)
            else:
                bm = bmesh.new()
                bm.from_mesh(mesh)

            bm.faces.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.normal_update()

            crease_layer = bm.edges.layers.float.get('crease_edge')
            if crease_layer is None:
                crease_layer = bm.edges.layers.float.new('crease_edge')

            if rprops.clear_existing_creases:
                for e in bm.edges:
                    e[crease_layer] = 0.0

            detected = 0
            for e in bm.edges:
                lf = e.link_faces
                is_boundary = False
                # Mesh boundary -- edge has one attached face
                if len(lf) == 1 and rprops.mark_boundary_as_crease:
                    is_boundary = True
                # Standard edge with 2 faces attached
                elif len(lf) == 2:
                    dot = max(-1.0, min(1.0, lf[0].normal.dot(lf[1].normal)))
                    angle_deg = math.degrees(math.acos(dot))
                    best_strength = 0.0
                    if getattr(rprops, 'threshold_mode', 'MULTI') == 'MULTI':
                        # Choose the strongest threshold whose angle is <= the edge angle
                        for item in sorted(rprops.thresholds, key=lambda t: float(t.angle_deg), reverse=True):
                            if angle_deg >= float(item.angle_deg):
                                best_strength = float(item.strength)
                                break
                    else:
                        # Single threshold mode
                        if angle_deg >= float(rprops.crease_angle_threshold):
                            best_strength = float(rprops.crease_strength)

                if is_boundary or best_strength > 0.0:
                    e[crease_layer] = 1.0 if is_boundary else best_strength
                    detected += 1

            if is_edit:
                bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
                bm = bmesh.from_edit_mesh(mesh)
                _sync_bmesh_edge_layer_to_mesh_attribute(mesh, bm, "crease_edge")
            else:
                bm.to_mesh(mesh)
                bm.free()
                mesh.update()
                bm2 = bmesh.new()
                bm2.from_mesh(mesh)
                _sync_bmesh_edge_layer_to_mesh_attribute(mesh, bm2, "crease_edge")
                bm2.free()

            # Update crease count stat on properties
            try:
                attr = mesh.attributes.get('crease_edge')
                if attr is not None:
                    values = [0.0] * len(mesh.edges)
                    attr.data.foreach_get("value", values)
                    crease_count = sum(1 for v in values if v > 0.0)
                    rprops.crease_count = int(crease_count)
            except Exception:
                pass

            self.report({'INFO'}, f"Creases set on {detected} edges")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Crease detection failed: {e}")
            return {'CANCELLED'}


class AUTO_REMESHER_OT_clear_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_creases"
    bl_label = "Clear Creases"
    bl_description = "Clear all edge creases on the selected mesh"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        mesh = obj.data
        try:
            is_edit = (obj.mode == 'EDIT')
            if is_edit:
                bm = bmesh.from_edit_mesh(mesh)
            else:
                bm = bmesh.new()
                bm.from_mesh(mesh)

            bm.edges.ensure_lookup_table()
            crease_layer = bm.edges.layers.float.get('crease_edge')
            if crease_layer is None:
                crease_layer = bm.edges.layers.float.new('crease_edge')
            for e in bm.edges:
                e[crease_layer] = 0.0

            if is_edit:
                bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
                bm = bmesh.from_edit_mesh(mesh)
                _sync_bmesh_edge_layer_to_mesh_attribute(mesh, bm, "crease_edge")
            else:
                bm.to_mesh(mesh)
                bm.free()
                mesh.update()
                bm2 = bmesh.new()
                bm2.from_mesh(mesh)
                _sync_bmesh_edge_layer_to_mesh_attribute(mesh, bm2, "crease_edge")
                bm2.free()

            # Reset crease count stat
            try:
                rprops.crease_count = 0
            except Exception:
                pass

            self.report({'INFO'}, "All creases cleared")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Clear creases failed: {e}")
            return {'CANCELLED'}


def _sync_bmesh_edge_layer_to_mesh_attribute(mesh, bm, layer_name="crease_edge"):
    bm.edges.index_update()
    crease_layer = bm.edges.layers.float.get(layer_name)
    if crease_layer is None:
        return
    attr = mesh.attributes.get(layer_name)
    if attr is None:
        attr = mesh.attributes.new(name=layer_name, type='FLOAT', domain='EDGE')
    values = [0.0] * len(mesh.edges)
    for e in bm.edges:
        values[e.index] = float(e[crease_layer])
    attr.data.foreach_set("value", values)


