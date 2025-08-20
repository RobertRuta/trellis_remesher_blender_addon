import math
import bpy
import bmesh
from array import array
from ..utils import props_accesor as p
from ..utils import mesh_attribute_accessor as mesh_attr


class AUTO_REMESHER_OT_detect_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.detect_creases"
    bl_label = "Detect Creases"
    bl_description = "Detect hard edges by dihedral angle and set edge crease layers"

    def execute(self, context):
        try:
            rprops     = p.get_rprops(context)
            mesh_obj   = p.get_mesh(context)
            thresholds = p.get_thresholds(context)
            mesh = mesh_obj.data
            
            is_edit = (mesh_obj.mode == 'EDIT')
            if is_edit:
                bm = bmesh.from_edit_mesh(mesh)
            else:
                bm = bmesh.new()
                bm.from_mesh(mesh)

            bm.faces.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.normal_update()

            # Init edge crease layer id data
            mesh_attr.set_edge_layer_ids(mesh, create=True)
            edge_crease_layer_buffer = mesh_attr.extract_edge_layer_ids(mesh)

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
                            detected_layer = int(threshold.layer_id)
                            break

                if is_boundary or detected_layer >= 0:
                    edge_crease_layer_buffer[e.index] = detected_layer
                    detected += 1
            
            # Set crease count in properties
            rprops.crease_count = detected
            
            mesh_attr.set_edge_layer_ids(mesh, create=False, data=edge_crease_layer_buffer)
            
            if mesh_obj.mode == 'EDIT':
                bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
            else:
                mesh.update()
                        
        except Exception as e:
            self.report({'ERROR'}, f"Crease detection failed: {e}")
            return {'CANCELLED'}

        # Auto-run visualiser after calculating creases
        try:
            bpy.ops.auto_remesher.vp_crease_vis()
        except Exception as e:
            self.report({'WARNING'}, f"Crease visualiser failed. Skipping...")
        
        self.report({'INFO'}, f"Crease layers set on {rprops.crease_count} edges")
        return {'FINISHED'}


class AUTO_REMESHER_OT_clear_creases(bpy.types.Operator):
    bl_idname = "auto_remesher.clear_creases"
    bl_label = "Clear Creases"
    bl_description = "Clear all edge crease layers on the selected mesh"

    def execute(self, context):
        try:
            rprops = p.get_rprops(context)
            mesh = p.get_mesh(context).data
            mesh_attr.set_edge_layer_ids(mesh, create=True)
            rprops.crease_count = 0
            self.report({'INFO'}, "Crease attribute cleared, and crease count reset.")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear creases: {e}")
            return {'CANCELLED'}