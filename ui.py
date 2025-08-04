import bpy
import subprocess


class AutoRemesherProperties(bpy.types.PropertyGroup):
    text_prompt: bpy.props.StringProperty(
        name="Text Prompt",
        description="Text prompt to send to TRELLIS",
        default=""
    )

    image: bpy.props.PointerProperty(
        name="Image Prompt",
        description="Image prompt to send to TRELLIS",
        type=bpy.types.Image
    )
    
    mesh: bpy.props.PointerProperty(
        name="Loaded Mesh",
        description="Loaded or generated mesh",
        type=bpy.types.Object
    )


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


class VIEW3D_PT_autoremesher_generator(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Generate Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher
        
        split1 = layout.split(factor=0.5, align=True)
        split1.label(text="Text Prompt:")
        split1.prop(props, "text_prompt", text="")
        split1.enabled = not bool(props.image)
        
        layout.label(text="OR", )
        
        split2 = layout.split(factor=0.5, align=True)
        split2.label(text="Image Prompt:")
        split2.template_ID(props, "image", open="image.open")
        split2.enabled = not bool(props.text_prompt.strip())

        row = layout.row()
        row.enabled = bool(props.text_prompt.strip()) or bool(props.image)
        row.operator("trellis.generate_mesh", icon='PLAY')


class VIEW3D_PT_autoremesher_loader(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Load Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher

        if props.mesh and props.mesh.type == 'MESH':
            box = layout.box()
            box.label(text=f"Name: {props.mesh.name}")
            box.label(text=f"Verts: {len(props.mesh.data.vertices)} | Faces: {len(props.mesh.data.polygons)}")
        else:
            layout.label(text="No mesh loaded yet.")
        
        layout.label(text="."*10000)
        
        row1 = layout.split(factor=0.5, align=True)
        row1.label(text="Select Existing:")
        row1.template_ID(props, "mesh")
        
        row2 = layout.split(factor=0.5, align=True)
        row2.label(text="Import Mesh:")
        row2.operator("auto_remesher.import_mesh", text="Open", icon='FILE_FOLDER')
        
        
class VIEW3D_PT_autoremesher_remesher(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Remesher"
    
    def draw(self, context):
        pass
        

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


classes = (
    AutoRemesherProperties,
    TRELLIS_OT_generate_mesh,
    AUTO_REMESHER_OT_import_mesh,
    VIEW3D_PT_autoremesher_generator,
    VIEW3D_PT_autoremesher_loader,
    VIEW3D_PT_autoremesher_remesher
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.auto_remesher = bpy.props.PointerProperty(type=AutoRemesherProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.auto_remesher