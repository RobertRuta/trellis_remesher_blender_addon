import bpy


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