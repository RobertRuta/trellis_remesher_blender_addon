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

        col.label(text="Prompt", icon='INFO')
        col.separator()
        prompt_mode_selector = col.row(align=True)
        prompt_mode_selector.alignment = 'EXPAND'
        prompt_mode_selector.prop(props, "prompt_mode", expand=True)
        prompt_mode_selector.separator()

        prompt_box = col.box()
        prompt_box.alignment = 'EXPAND'
        prompt_box.separator()
        # row = prompt_box.row()
        # row.separator()
        if props.prompt_mode == 'TEXT':
            prompt_box.prop(props, "text_prompt", text="")
        elif props.prompt_mode == 'IMAGE':
            prompt_box.template_ID(props, "image_prompt", open="image.open")
        
        prompt_box.separator()

        col.separator()
        col.separator()

        # Enable only if valid input
        generate_row = col.row()
        generate_row.scale_x = 1.5
        generate_row.alignment = 'CENTER'
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
