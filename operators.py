import bpy
from . import utils


class TRELLIS_OT_generate_mesh(bpy.types.Operator):
    bl_idname = "trellis.generate_mesh"
    bl_label = "Generate"
    bl_description = "Run the TRELLIS generator subprocess"

    def execute(self, context):
        props = context.scene.auto_remesher
        props_dict = {
            "text_prompt": props.text_prompt.strip(), 
            "image_prompt": props.image_prompt
        }
        
        try:
            mesh = utils.try_generate_mesh(props_dict)
            props.mesh = mesh
            self.report({'INFO'}, "TRELLIS backend successfully generated mesh.")
            print("TRELLIS backend successfully generated mesh.")
        except Exception as e:
            self.report({'ERROR'}, f"TRELLIS backend failed to generate mesh: {e}")
            print(e.stderr)
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
        ext = self.filepath.lower()
        if ext.endswith(".obj"):
            bpy.ops.import_scene.obj(filepath=self.filepath)
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
        
        # Assume last imported object is active
        obj = context.selected_objects[-1]
        context.scene.auto_remesher.mesh = obj
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}