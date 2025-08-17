# import bpy
# from ..utils import center_label


# class VIEW3D_PT_autormesher_api_settings(bpy.types.Panel):
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Auto Remesher"
#     bl_label = "Trellis Connection"

#     def draw(self, context):
#         props = context.scene.auto_remesher
#         sprops = props.server
#         layout = self.layout
        
#         # SERVER CONFIG BOX
#         server_box = layout.box()
#         server_box.label(text="Server Configuration", icon='PREFERENCES')
        
#         url_row = server_box.split(factor=0.3, align=True)
#         url_row.label(text="API URL:")
#         url_box = url_row.box()
#         url_box.label(text=sprops.api_url)
        
#         server_box.prop(sprops, "advanced_server_config")
        
#         if sprops.advanced_server_config:
#             advanced_settings_box = server_box.box()
#             advanced_settings_box.prop(sprops, "server_host", text="Host")
#             advanced_settings_box.prop(sprops, "server_port", text="Port")

#         # CHECK CONNECTION
#         check_row = server_box.row()
#         check_row.operator("trellis.check_connection", text="Check Connection", icon='URL')
#         check_row.label(text=sprops.connection_status)


# class VIEW3D_PT_autoremesher_generator(bpy.types.Panel):
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Auto Remesher"
#     bl_label = "Generate Mesh"

#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.auto_remesher
#         gprops = props.generator

#         box = layout.box()
#         col = box.column(align=True)

#         col.label(text="Prompt", icon='INFO')
#         col.separator()
#         prompt_mode_selector = col.row(align=True)
#         prompt_mode_selector.alignment = 'EXPAND'
#         prompt_mode_selector.prop(gprops, "prompt_mode", expand=True)
#         prompt_mode_selector.separator()
#         if gprops.prompt_mode == 'TEXT':
#             quality_settings = col.row(align=True)
#             quality_settings.label(text="Quality:")
#             quality_settings.prop(gprops, "generation_quality", expand=True)

#         prompt_box = col.box()
#         prompt_box.alignment = 'EXPAND'
#         prompt_box.separator()
#         # row = prompt_box.row()
#         # row.separator()
#         if gprops.prompt_mode == 'TEXT':
#             prompt_box.prop(gprops, "text_prompt", text="")
#         elif gprops.prompt_mode == 'IMAGE':
#             prompt_box.template_ID(gprops, "image", open="image.open")
        
#         prompt_box.separator()

#         col.separator()
#         col.separator()

#         # Enable only if valid input
#         generate_row = col.row()
#         generate_row.scale_x = 1.5
#         generate_row.alignment = 'CENTER'
#         generate_row.operator("trellis.generate_mesh", text="GENERATE", icon='PLAY')
#         generate_row.enabled = not ((gprops.prompt_mode == 'TEXT' and len(gprops.text_prompt) == 0) 
#                                     or (gprops.prompt_mode == 'IMAGE' and len(gprops.image_path) == 0))
#         col.separator()
#         col.separator()


# class VIEW3D_PT_autoremesher_loader(bpy.types.Panel):
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Auto Remesher"
#     bl_label = "Load Mesh"

#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.auto_remesher
#         rprops = props.remesher

#         mesh_info_box = layout.box()
#         mesh_info_label = mesh_info_box.column(align=True)
#         mesh_info_label.label(text="Loaded Mesh Info", icon='OBJECT_DATA')
#         mesh_data_row = mesh_info_box.row(align=True)
#         mesh_data_row.alignment = 'CENTER'
#         if rprops.mesh and getattr(rprops.mesh, "type", None) == 'MESH':
#             mesh_data_box = mesh_data_row.box()
#             mesh_data_box.label(text=f"Name: {rprops.mesh.name}")
#             mesh_data_box.label(text=f"Verts: {len(rprops.mesh.data.vertices)}")
#             mesh_data_box.label(text=f"Faces: {len(rprops.mesh.data.polygons)}")
#         else:
#             mesh_data_row.label(text="No mesh loaded yet.", icon='INFO')
#             mesh_data_row.enabled = False

#         layout.separator()

#         row1 = layout.row(align=True)
#         row1.label(text="Select Existing Mesh:")
#         row1.template_ID(rprops, "mesh")

#         layout.separator()

#         row2 = layout.row(align=True)
#         row2.label(text="Import New Mesh:")
#         row2.operator("auto_remesher.import_mesh", text="Open", icon='FILE_FOLDER')


# class VIEW3D_PT_autoremesher_remesher(bpy.types.Panel):
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Auto Remesher"
#     bl_label = "Remesher"

#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.auto_remesher
#         rprops = props.remesher
        
#         thresholds = [rprops.single_threshold] if rprops.is_single_threshold else rprops.multi_thresholds
#         crease_count = rprops.crease_count
#         selected_layer = rprops.active_crease_layer_display

#         ######################## Creasing Box ########################
        
#         crease_definiton_box = layout.box()
#         crease_title_row = crease_definiton_box.row()
#         crease_title_row.alignment = 'CENTER'
#         crease_title_row.label(text="Creasing", icon='MOD_BEVEL')
        
#         crease_definiton_box.separator()
        
#         ############ Auto Crease Detection Box ############
        
#         auto_detect_section = crease_definiton_box.box()
#         auto_detect_title_row = auto_detect_section.row()
#         auto_detect_title_row.alignment = 'CENTER'
#         auto_detect_title_row.label(text="Auto Crease Detection", icon='PRESET')
        
#         if not rprops.mesh or getattr(rprops.mesh, "type", None) != 'MESH':
#             auto_detect_section.label(text="No mesh loaded yet.", icon='INFO')
#             auto_detect_section.enabled = False
#             return
        
#         ###### Auto Crease Detection Info Box ######
#         info = auto_detect_section.box()

#         info.label(text="Info", icon="INFO_LARGE")
#         center_label(info, f"Target Mesh: {rprops.mesh.name}")
#         center_label(info, f"Crease Count: {crease_count}")
#         center_label(info, f"Crease Layers: {len(thresholds)}")

#         settings_section = auto_detect_section.box()
#         settings_section.label(text="Settings", icon="SETTINGS")
#         settings_section.prop(rprops, "mark_boundary_as_crease")
        
#         ###### Single / Multi-Threshold Selector ######
#         layers_col = settings_section.column(align=True)
#         mode_row = layers_col.row(align=True)
#         mode_row.alignment = 'EXPAND'
#         # "Single" button
#         mode_row.operator("auto_remesher.set_threshold_mode", text="Single", depress=rprops.is_single_threshold).use_single = True
#         # "Multi" button
#         mode_row.operator("auto_remesher.set_threshold_mode", text="Multi", depress=not rprops.is_single_threshold).use_single = False
#         # thresholds_section = settings_section.box()
#         layers_col.separator()
#         ### Single Threshold Config ###
#         if rprops.is_single_threshold:
#             single_box = layers_col.box()
#             single_box.prop(rprops, "crease_angle_threshold")
#             single_box.prop(rprops, "single_threshold_color")
#             gen_row = single_box.row()
#             gen_row.operator("auto_remesher.generate_finer_detail", text="Show Finer Detail", icon='DECORATE_OVERRIDE')
#         ### Multi-Thresholds Config ###
#         else:
#             layers_col.label(text="Thresholds:")
#             list_row = layers_col.row()
#             list_row.template_list("AUTO_REMESHER_UL_thresholds", "", rprops, "multi_thresholds", rprops, "thresholds_index", rows=3)
#             list_ops = list_row.column(align=True)
#             list_ops.operator("auto_remesher.threshold_add", icon='ADD', text="")
#             list_ops.operator("auto_remesher.threshold_remove", icon='REMOVE', text="")

#         ### Run / Clear Crease Detction Buttons ###
#         run_detect_box = auto_detect_section.box()
#         run_detect_box.label(text="Run", icon="PLAY")
#         run_auto_detect_row = run_detect_box.row()
#         run_label_txt = "Recalculate" if crease_count > 0 else "Detect Creases"            
#         run_auto_detect_row.operator("auto_remesher.detect_creases", text=run_label_txt, icon='MEMORY')
#         if crease_count > 0:
#             run_auto_detect_row.operator("auto_remesher.clear_creases", text="Clear", icon='X')
        
#         crease_definiton_box.separator()
        
#         ############ Crease Visualisation Box ############
        
#         ###### Vertex Paint Visualisation Box ######
#         crease_vis_section = crease_definiton_box.box()
#         center_label(crease_vis_section, text="Crease Visualiser", icon="VPAINT_HLT")
        
#         ### Crease Visualisation Info Box ###
#         info_vis_box = crease_vis_section.box()
#         info_vis_box.label(text="Info", icon="INFO_LARGE")
#         center_label(info_vis_box, f"Crease layers: {len(thresholds)}")
#         center_label(info_vis_box, f"Selected layers: {rprops.active_crease_layer_display + 1 if rprops.active_crease_layer_display >= 0 else 'All'}")
#         drawn_layer_count = 0
#         if selected_layer == -1:
#             drawn_layer_count = len(thresholds)
#         elif rprops.accumulate_lower_layers:
#             drawn_layer_count = selected_layer + 1
#         else:
#             drawn_layer_count = 1
#         center_label(info_vis_box, f"Layers drawn: {drawn_layer_count}")
        
#         # ### Crease Visualisation Settings Box ###
#         # settings_vis_box = crease_vis_section.box()
#         # settings_vis_box.label(text="Settings", icon="SETTINGS")
        
#         ### Layer Switcher ###
#         # Accumulate Previous Layers Switch
#         layer_selector_box = crease_vis_section.box()
#         layer_selector_box.label(text="Display Layer", icon="SEQ_STRIP_DUPLICATE")
#         layer_selector_box.prop(rprops, "accumulate_lower_layers")
        
#         # "All" button on its own row
#         all_row = layer_selector_box.row()
#         all_btn = all_row.operator("auto_remesher.change_visible_layers", text="All")
#         all_btn.display_layer_index = -1
#         if rprops.active_crease_layer_display != -1:
#             all_row.active = False
        
#         # Layers arranged in a column
#         layers_col = layer_selector_box.column(align=True)
#         layers_col.label(text="Thresholds:")
#         list_row = layers_col.row()
#         list_row.template_list("AUTO_REMESHER_UL_layers", "", rprops, "crease_layers", rprops, "crease_layers_index", rows=4)
#         list_ops = list_row.column(align=True)
#         # list_ops.operator("auto_remesher.threshold_add", icon='ADD', text="")
#         # list_ops.operator("auto_remesher.threshold_remove", icon='REMOVE', text="")
        
#         ### Crease Visualisation Run Box ###
#         run_vis_box = crease_vis_section.box()
#         run_vis_box.label(text="Run", icon="PLAY")
#         run_visualisation_row = run_vis_box.row()
#         run_visualisation_row.operator("auto_remesher.vp_crease_vis", text="Visualise", icon='PLAY')
#         run_visualisation_row.operator("auto_remesher.clear_vp_vis", text="Clear", icon='X')