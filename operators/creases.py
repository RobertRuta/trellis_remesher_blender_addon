import math
import bpy
import bmesh
from array import array


class AUTO_REMESHER_OT_detect_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.detect_creases"
    bl_label = "Detect Creases"
    bl_description = "Detect hard edges by dihedral angle and set edge crease layers"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher

        # Get mesh
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}
        
        # Preparing crease angle thresholds
        thresholds = [rprops.single_threshold] if rprops.is_single_threshold else rprops.multi_thresholds
        threshold_count = len(thresholds)
        if thresholds is None or threshold_count < 1:
            self.report({'ERROR'}, "No thresholds provided")
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

            crease_layer_attr_name = 'crease_layer'
            crease_layer_attr = mesh.attributes.get(crease_layer_attr_name)
            if crease_layer_attr is None:
                crease_layer_attr = mesh.attributes.new(crease_layer_attr_name, type='INT8', domain='EDGE')
            
            edge_crease_layer_buffer = array('b', [-1] * len(mesh.edges))

            # Iterate over edges in mesh and set crease layer
            detected = 0
            for e in bm.edges:
                detected_layer = -1  # -1 means no layer assigned
                is_boundary = False
                attached_faces = e.link_faces
                
                # Mesh boundary -- edge has one attached face
                if len(attached_faces) == 1 and rprops.mark_boundary_as_crease:
                    is_boundary = True
                    detected_layer = 0  # Boundary edges get layer 0
                # Standard edge with 2 faces attached
                elif len(attached_faces) == 2:
                    # Calculate angle between attached faces
                    dot = max(-1.0, min(1.0, attached_faces[0].normal.dot(attached_faces[1].normal)))
                    angle_deg = math.degrees(math.acos(dot))
                    
                    # Find the lowest layer number (largest angle) that matches this edge
                    for threshold in thresholds:
                        if angle_deg >= float(threshold.angle_deg):
                            detected_layer = int(threshold.layer_number)
                            break

                if is_boundary or detected_layer >= 0:
                    edge_crease_layer_buffer[e.index] = detected_layer
                    detected += 1
            
            # Set crease count in properties
            rprops.crease_count = detected
            
            crease_layer_attr.data.foreach_set("value", edge_crease_layer_buffer)
            
            if obj.mode == 'EDIT':
                bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            else:
                mesh.update()
                
            self.report({'INFO'}, f"Crease layers set on {rprops.crease_count} edges")
        except Exception as e:
            self.report({'ERROR'}, f"Crease detection failed: {e}")
            return {'CANCELLED'}

        # Auto-run visualiser after calculating creases
        bpy.ops.auto_remesher.vp_crease_vis()
        return {'FINISHED'}


class AUTO_REMESHER_OT_clear_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_creases"
    bl_label = "Clear Creases"
    bl_description = "Clear all edge crease layers on the selected mesh"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        if rprops.crease_count == 0:
            self.report({'INFO'}, "No creases to clear")
            return {'FINISHED'}

        try:
            mesh = obj.data
            crease_layer_attr = mesh.attributes.get('crease_layer')
            crease_layer_attr.data.foreach_set("value", [-1]*len(mesh.edges))

            self.report({'INFO'}, "All crease layers cleared")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear creases: {e}")
            return {'CANCELLED'}