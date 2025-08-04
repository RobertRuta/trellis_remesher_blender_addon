import bpy


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