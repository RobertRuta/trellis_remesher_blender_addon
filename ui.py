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


class VIEW3D_PT_autoremesher_loader(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Generate Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher
        
        split1 = layout.split(factor=0.3, align=True)
        split1.label(text="Text Prompt:")
        split1.prop(props, "text_prompt", text="")
        split1.enabled = not bool(props.image)
        
        layout.label(text="OR", )
        
        split2 = layout.split(factor=0.3, align=True)
        split2.label(text="Image Prompt:")
        split2.template_ID(props, "image", open="image.open")
        split2.enabled = not bool(props.text_prompt.strip())
        

        row = layout.row()
        row.enabled = bool(props.text_prompt.strip()) or bool(props.image)
        row.operator("trellis.generate_mesh", icon='PLAY')


classes = (
    AutoRemesherProperties,
    TRELLIS_OT_generate_mesh,
    VIEW3D_PT_autoremesher_loader,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.auto_remesher = bpy.props.PointerProperty(type=AutoRemesherProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.auto_remesher