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

            threshold_rad = math.radians(rprops.crease_angle_threshold)
            strength = rprops.crease_strength

            detected = 0
            for e in bm.edges:
                lf = e.link_faces
                mark = False
                if len(lf) == 2:
                    dot = max(-1.0, min(1.0, lf[0].normal.dot(lf[1].normal)))
                    angle = math.acos(dot)
                    if angle >= threshold_rad:
                        mark = True
                elif len(lf) == 1 and rprops.mark_boundary_as_crease:
                    mark = True

                if mark:
                    current = e[crease_layer]
                    if current < strength:
                        e[crease_layer] = strength
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


