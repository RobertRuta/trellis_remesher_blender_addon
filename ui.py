import bpy


class VIEW3D_PT_autormesher_api(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Trellis Connection"

    def draw(self, context):
        props = context.scene.auto_remesher
        layout = self.layout
        
        # SERVER CONFIG BOX
        server_box = layout.box()
        server_box.label(text="Server Configuration", icon='PREFERENCES')
        
        url_row = server_box.split(factor=0.3, align=True)
        url_row.label(text="API URL:")
        url_box = url_row.box()
        url_box.label(text=props.api_url)
        
        server_box.prop(props, "advanced_server_config")
        
        if props.advanced_server_config:
            advanced_settings_box = server_box.box()
            advanced_settings_box.prop(props, "server_host", text="Host")
            advanced_settings_box.prop(props, "server_port", text="Port")

        # CHECK CONNECTION
        check_row = server_box.row()
        check_row.operator("trellis.check_connection", text="Check Connection", icon='URL')
        check_row.label(text=props.connection_status)


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
            prompt_box.template_ID(props, "image", open="image.open")
        
        prompt_box.separator()

        col.separator()
        col.separator()

        # Enable only if valid input
        generate_row = col.row()
        generate_row.scale_x = 1.5
        generate_row.alignment = 'CENTER'
        generate_row.operator("trellis.generate_mesh", text="GENERATE", icon='PLAY')
        generate_row.enabled = not ((props.prompt_mode == 'TEXT' and len(props.text_prompt) == 0) 
                                    or (props.prompt_mode == 'IMAGE' and len(props.image_path) == 0))
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

        mesh_info_box = layout.box()
        mesh_info_label = mesh_info_box.column(align=True)
        mesh_info_label.label(text="Loaded Mesh Info", icon='OBJECT_DATA')
        mesh_data_row = mesh_info_box.row(align=True)
        mesh_data_row.alignment = 'CENTER'
        if props.mesh and getattr(props.mesh, "type", None) == 'MESH':
            mesh_data_box = mesh_data_row.box()
            mesh_data_box.label(text=f"Name: {props.mesh.name}")
            mesh_data_box.label(text=f"Verts: {len(props.mesh.data.vertices)}")
            mesh_data_box.label(text=f"Faces: {len(props.mesh.data.polygons)}")
        else:
            mesh_data_row.label(text="No mesh loaded yet.", icon='INFO')
            mesh_data_row.enabled = False

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
