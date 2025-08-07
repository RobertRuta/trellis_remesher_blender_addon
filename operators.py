import bpy
from . import utils


class TRELLIS_OT_generate_mesh(bpy.types.Operator):
    bl_idname = "trellis.generate_mesh"
    bl_label = "Generate"
    bl_description = "Run the TRELLIS generator subprocess"

    def execute(self, context):
        props = context.scene.auto_remesher
        
        if props.prompt_mode == 'TEXT':
            props.image_prompt = None
        elif props.prompt_mode == 'IMAGE':
            props.text_prompt = ''

        props_dict = {
            "text_prompt": props.text_prompt.strip(), 
            "image_prompt": props.image_path
        }
        
        try:
            mesh = utils.send_mesh_generation_request(props_dict)
            props.mesh = mesh
            self.report({'INFO'}, "TRELLIS backend successfully generated mesh.")
            print("TRELLIS backend successfully generated mesh.")
        except Exception as e:
            self.report({'ERROR'}, f"TRELLIS backend failed to generate mesh: {e}")
            print(e)
        return {'FINISHED'}
    
    
class AUTO_REMESHER_OT_import_mesh(bpy.types.Operator):
    bl_idname = "auto_remesher.import_mesh"
    bl_label = "Import Mesh"
    bl_description = "Import a mesh file and set it as the target."
    
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(
        default="*.obj;*.fbx;*.glb;*.gltf;*.ply;*.stl",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        # Capture existing objects before import
        before = set(bpy.data.objects)

        # Run the appropriate import operator
        ext = self.filepath.lower()
        if ext.endswith(".obj"):
            # bpy.ops.import_scene.obj(filepath=self.filepath)
            self.report({'ERROR'}, "Obj not supported yet")
            return {'CANCELLED'}
        elif ext.endswith(".fbx"):
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        elif ext.endswith(".glb") or ext.endswith(".gltf"):
            bpy.ops.import_scene.gltf(filepath=self.filepath)
        elif ext.endswith(".ply"):
            bpy.ops.import_mesh.ply(filepath=self.filepath)
        elif ext.endswith(".stl"):
            bpy.ops.import_mesh.stl(filepath=self.filepath)
        else:
            self.report({'ERROR'}, "Unsupported file type")
            return {'CANCELLED'}
        
        # Identify newly imported objects
        after = set(bpy.data.objects)
        new_objects = list(after - before)
        if not new_objects:
            self.report({'ERROR'}, "No mesh imported")
            return {'CANCELLED'}

        # Try to find the main mesh object among the new ones
        new_meshes = [obj for obj in new_objects if obj.type == 'MESH']
        if not new_meshes:
            self.report({'ERROR'}, "No mesh object found in import")
            return {'CANCELLED'}

        imported_obj = new_meshes[-1]  # Or first(), or whatever logic you prefer

        # Ensure the object is selected and visible
        bpy.ops.object.select_all(action='DESELECT')
        imported_obj.select_set(True)
        context.view_layer.objects.active = imported_obj

        # Set the imported object as the remesher target
        context.scene.auto_remesher.mesh = imported_obj
        return {'FINISHED'}

    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    
class TRELLIS_OT_check_connection(bpy.types.Operator):
    bl_idname = "trellis.check_connection"
    bl_label = "Check Connection"

    def execute(self, context):
        props = context.scene.auto_remesher

        import requests
        try:
            url = props.api_url
            resp = requests.get(f"{url}/status", timeout=2)
            if resp.status_code == 200:
                props.connection_status = "✅ Connected"
            else:
                props.connection_status = f"⚠ Error {resp.status_code}"
        except Exception as e:
            props.connection_status = f"❌ {str(e)}"
        return {'FINISHED'}