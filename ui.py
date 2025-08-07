import bpy


class VIEW3D_PT_autoremesher_generator(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Generate Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher

        box = layout.box()
        col = box.column(align=True)

        col.label(text="Prompt Input", icon='INFO')
        col.separator()
        col.separator()

        text_box = col.box()
        text_label = text_box.row(align=True)
        # text_label.alignment = 'CENTER'
        text_label.label(text="Text Prompt:")
        text_input_field = text_box.row(align=True)
        text_input_field.prop(props, "text_prompt", text="")
        text_box.enabled = not bool(props.image_prompt)
        text_box.separator()
        
        col.separator()
        or_separator = col.row()
        or_separator.alignment = 'CENTER'
        or_separator.label(text="or", icon='ARROW_LEFTRIGHT')
        col.separator()

        image_box = col.box()
        image_label = image_box.row(align=True)
        # image_label.alignment = 'CENTER'
        image_label.label(text="Image Prompt:")
        image_prompt_selector = image_box.row(align=True)
        image_prompt_selector.template_ID(props, "image_prompt", open="image.open")
        image_box.enabled = not bool(props.text_prompt.strip())
        image_box.separator()

        col.separator()
        col.separator()
        col.separator()
        generate_row = col.row()
        generate_row.alignment = 'CENTER'
        generate_row.enabled = bool(props.text_prompt.strip()) or bool(props.image_prompt)
        generate_row.operator("trellis.generate_mesh", text="GENERATE", icon='PLAY')
        col.separator()
        col.separator()


class VIEW3D_PT_autoremesher_loader(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Load Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Loaded Mesh Info", icon='OBJECT_DATA')

        if props.mesh and props.mesh.type == 'MESH':
            mesh_box = col.box()
            mesh_box.label(text=f"Name: {props.mesh.name}")
            mesh_box.label(text=f"Verts: {len(props.mesh.data.vertices)}")
            mesh_box.label(text=f"Faces: {len(props.mesh.data.polygons)}")
        else:
            col.label(text="No mesh loaded yet.", icon='INFO')

        layout.separator()

        row1 = layout.row(align=True)
        row1.label(text="Select Existing Mesh:")
        row1.template_ID(props, "mesh")

        layout.separator()

        row2 = layout.row(align=True)
        row2.label(text="Import New Mesh:")
        row2.operator("auto_remesher.import_mesh", text="Open", icon='FILE_FOLDER')


        
class VIEW3D_PT_autoremesher_remesher(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Remesher"

    def draw(self, context):
        layout = self.layout
        layout.label(text="(Remeshing tools coming soon)", icon='MOD_REMESH')
