import bpy


class VIEW3D_PT_autormesher_api_settings(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Trellis Connection"

    def draw(self, context):
        props = context.scene.auto_remesher
        sprops = props.server
        layout = self.layout
        
        # SERVER CONFIG BOX
        server_box = layout.box()
        server_box.label(text="Server Configuration", icon='PREFERENCES')
        
        url_row = server_box.split(factor=0.3, align=True)
        url_row.label(text="API URL:")
        url_box = url_row.box()
        url_box.label(text=sprops.api_url)
        
        server_box.prop(sprops, "advanced_server_config")
        
        if sprops.advanced_server_config:
            advanced_settings_box = server_box.box()
            advanced_settings_box.prop(sprops, "server_host", text="Host")
            advanced_settings_box.prop(sprops, "server_port", text="Port")

        # CHECK CONNECTION
        check_row = server_box.row()
        check_row.operator("trellis.check_connection", text="Check Connection", icon='URL')
        check_row.label(text=sprops.connection_status)


class VIEW3D_PT_autoremesher_generator(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Generate Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher
        gprops = props.generator

        box = layout.box()
        col = box.column(align=True)

        col.label(text="Prompt", icon='INFO')
        col.separator()
        prompt_mode_selector = col.row(align=True)
        prompt_mode_selector.alignment = 'EXPAND'
        prompt_mode_selector.prop(gprops, "prompt_mode", expand=True)
        prompt_mode_selector.separator()
        if gprops.prompt_mode == 'TEXT':
            quality_settings = col.row(align=True)
            quality_settings.label(text="Quality:")
            quality_settings.prop(gprops, "generation_quality", expand=True)

        prompt_box = col.box()
        prompt_box.alignment = 'EXPAND'
        prompt_box.separator()
        # row = prompt_box.row()
        # row.separator()
        if gprops.prompt_mode == 'TEXT':
            prompt_box.prop(gprops, "text_prompt", text="")
        elif gprops.prompt_mode == 'IMAGE':
            prompt_box.template_ID(gprops, "image", open="image.open")
        
        prompt_box.separator()

        col.separator()
        col.separator()

        # Enable only if valid input
        generate_row = col.row()
        generate_row.scale_x = 1.5
        generate_row.alignment = 'CENTER'
        generate_row.operator("trellis.generate_mesh", text="GENERATE", icon='PLAY')
        generate_row.enabled = not ((gprops.prompt_mode == 'TEXT' and len(gprops.text_prompt) == 0) 
                                    or (gprops.prompt_mode == 'IMAGE' and len(gprops.image_path) == 0))
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
        rprops = props.remesher

        mesh_info_box = layout.box()
        mesh_info_label = mesh_info_box.column(align=True)
        mesh_info_label.label(text="Loaded Mesh Info", icon='OBJECT_DATA')
        mesh_data_row = mesh_info_box.row(align=True)
        mesh_data_row.alignment = 'CENTER'
        if rprops.mesh and getattr(rprops.mesh, "type", None) == 'MESH':
            mesh_data_box = mesh_data_row.box()
            mesh_data_box.label(text=f"Name: {rprops.mesh.name}")
            mesh_data_box.label(text=f"Verts: {len(rprops.mesh.data.vertices)}")
            mesh_data_box.label(text=f"Faces: {len(rprops.mesh.data.polygons)}")
        else:
            mesh_data_row.label(text="No mesh loaded yet.", icon='INFO')
            mesh_data_row.enabled = False

        layout.separator()

        row1 = layout.row(align=True)
        row1.label(text="Select Existing Mesh:")
        row1.template_ID(rprops, "mesh")

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
        props = context.scene.auto_remesher
        rprops = props.remesher

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Auto Crease Detection", icon='MOD_BEVEL')

        if not rprops.mesh or getattr(rprops.mesh, "type", None) != 'MESH':
            col.label(text="No mesh loaded yet.", icon='INFO')
            col.enabled = False
            return

        info = col.box()
        info.label(text=f"Target: {rprops.mesh.name}")
        info.label(text=f"Verts: {len(rprops.mesh.data.vertices)}  Faces: {len(rprops.mesh.data.polygons)}")

        col.prop(rprops, "crease_angle_threshold")
        col.prop(rprops, "crease_strength")
        col.prop(rprops, "mark_boundary_as_crease")
        col.prop(rprops, "clear_existing_creases")

        row = col.row(align=True)
        row.operator("auto_remesher.detect_creases", text="Detect Creases", icon='SELECT_DIFFERENCE')
        row.operator("auto_remesher.clear_creases", text="Clear", icon='X')

        col.separator()
        col.prop(rprops, "show_crease_viz")
        col.prop(rprops, "viz_threshold")
        col.prop(rprops, "viz_thickness")
        
        # Geometry Nodes visualization
        gn_box = col.box()
        gn_box.label(text="Geometry Nodes Visualization", icon='NODETREE')
        gn_box.operator("auto_remesher.gn_crease_vis", text="Apply GN Visualisation", icon='SHADING_WIRE')
        
        # Vertex Paint visualization
        vp_box = col.box()
        vp_box.label(text="Vertex Paint Visualization", icon='VPAINT_HLT')
        vp_row = vp_box.row(align=True)
        vp_row.operator("auto_remesher.vp_crease_vis", text="Apply VP Visualisation", icon='VPAINT_HLT')
        vp_row.operator("auto_remesher.clear_vp_vis", text="Clear", icon='X')