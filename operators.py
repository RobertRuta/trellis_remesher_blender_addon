import bpy
import subprocess


class TRELLIS_OT_generate_mesh(bpy.types.Operator):
    bl_idname = "trellis.generate_mesh"
    bl_label = "Generate"
    bl_description = "Run the TRELLIS generator subprocess"

    def execute(self, context):
        script_path = "C:/Users/rober/_projects/TRELLIS/run_generate.py"
        try:
            result = subprocess.run(
                ["python", script_path],
                check=True,
                capture_output=True,
                text=True
            )
            self.report({'INFO'}, "TRELLIS generation completed.")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Subprocess failed: {e}")
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