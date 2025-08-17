import bpy
from ..utils import center_label


class VIEW3D_PT_autoremesher_remesher(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Remesher"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher
        rprops = props.remesher
        
        thresholds = [rprops.single_threshold] if rprops.is_single_threshold else rprops.multi_thresholds
        crease_count = rprops.crease_count

        ######################## Creasing Box ########################
        
        crease_definiton_box = layout.box()
        crease_title_row = crease_definiton_box.row()
        crease_title_row.alignment = 'CENTER'
        crease_title_row.label(text="Creasing", icon='MOD_BEVEL')
        
        crease_definiton_box.separator()
        
        ############ Auto Crease Detection Box ############
        self.draw_auto_crease(rprops, thresholds, crease_count, crease_definiton_box)
        
        crease_definiton_box.separator()
        
        ############ Crease Visualisation Box ############
        self.draw_crease_painter(rprops, thresholds, crease_count, crease_definiton_box)
    

    def draw_auto_crease(self, rprops, thresholds, crease_count, crease_definiton_box):
        auto_detect_section = crease_definiton_box.box()
        auto_detect_title_row = auto_detect_section.row()
        auto_detect_title_row.alignment = 'CENTER'
        auto_detect_title_row.label(text="Auto Crease Detection", icon='PRESET')
        
        if not rprops.mesh or getattr(rprops.mesh, "type", None) != 'MESH':
            auto_detect_section.label(text="No mesh loaded yet.", icon='INFO')
            auto_detect_section.enabled = False
            return
        
        ###### Auto Crease Detection Info Box ######
        info = auto_detect_section.box()

        info.label(text="Info", icon="INFO_LARGE")
        center_label(info, f"Target Mesh: {rprops.mesh.name}")
        center_label(info, f"Crease Count: {crease_count}")
        center_label(info, f"Crease Layers: {len(thresholds)}")

        settings_section = auto_detect_section.box()
        settings_section.label(text="Settings", icon="SETTINGS")
        settings_section.prop(rprops, "mark_boundary_as_crease")
        
        ###### Single / Multi-Threshold Selector ######
        layers_col = settings_section.column(align=True)
        mode_row = layers_col.row(align=True)
        mode_row.alignment = 'EXPAND'
        # "Single" button
        mode_row.operator("auto_remesher.set_threshold_mode", text="Single", depress=rprops.is_single_threshold).use_single = True
        # "Multi" button
        mode_row.operator("auto_remesher.set_threshold_mode", text="Multi", depress=not rprops.is_single_threshold).use_single = False
        # thresholds_section = settings_section.box()
        layers_col.separator()
        ### Single Threshold Config ###
        if rprops.is_single_threshold:
            single_box = layers_col.box()
            single_box.prop(rprops, "crease_angle_threshold")
            single_box.prop(rprops, "single_threshold_color")
            gen_row = single_box.row()
            gen_row.operator("auto_remesher.generate_finer_detail", text="Show Finer Detail", icon='DECORATE_OVERRIDE')
        ### Multi-Thresholds Config ###
        else:
            layers_col.label(text="Thresholds:")
            list_row = layers_col.row()
            list_row.template_list("AUTO_REMESHER_UL_thresholds", "", rprops, "multi_thresholds", rprops, "thresholds_index", rows=3)
            list_ops = list_row.column(align=True)
            list_ops.operator("auto_remesher.threshold_add", icon='ADD', text="")
            list_ops.operator("auto_remesher.threshold_remove", icon='REMOVE', text="")

        ### Run / Clear Crease Detction Buttons ###
        run_detect_box = auto_detect_section.box()
        run_detect_box.label(text="Run", icon="PLAY")
        run_auto_detect_row = run_detect_box.row()
        run_label_txt = "Recalculate" if crease_count > 0 else "Detect Creases"            
        run_auto_detect_row.operator("auto_remesher.detect_creases", text=run_label_txt, icon='MEMORY')
        if crease_count > 0:
            run_auto_detect_row.operator("auto_remesher.clear_creases", text="Clear", icon='X')
            
            
    def draw_crease_painter(self, rprops, thresholds, crease_count, ui_parent):
        ###### Vertex Paint Visualisation Box ######
        crease_vis_section = ui_parent.box()
        center_label(crease_vis_section, text="Crease Visualiser", icon="VPAINT_HLT")
        
        ### Crease Visualisation Info Box ###
        info_vis_box = crease_vis_section.box()
        info_vis_box.label(text="Info", icon="INFO_LARGE")
        center_label(info_vis_box, f"Crease layers: {len(thresholds)}")
        center_label(info_vis_box, f"Selected layers: {rprops.active_crease_layer_display + 1 if rprops.active_crease_layer_display >= 0 else 'All'}")
        drawn_layer_count = 0
        
        selected_layer = rprops.active_crease_layer_display
        if selected_layer == -1:
            drawn_layer_count = len(thresholds)
        elif rprops.accumulate_lower_layers:
            drawn_layer_count = selected_layer + 1
        else:
            drawn_layer_count = 1
        center_label(info_vis_box, f"Layers drawn: {drawn_layer_count}")
        
        # ### Crease Visualisation Settings Box ###
        # settings_vis_box = crease_vis_section.box()
        # settings_vis_box.label(text="Settings", icon="SETTINGS")
        
        ### Layer Switcher ###
        # Accumulate Previous Layers Switch
        layer_selector_box = crease_vis_section.box()
        layer_selector_box.label(text="Display Layer", icon="SEQ_STRIP_DUPLICATE")
        layer_selector_box.prop(rprops, "accumulate_lower_layers")
        
        # "All" button on its own row
        all_row = layer_selector_box.row()
        all_btn = all_row.operator("auto_remesher.change_visible_layers", text="All")
        if rprops.active_crease_layer_display != -1:
            all_row.active = False
        
        # Layers arranged in a column
        layers_col = layer_selector_box.column(align=True)
        layers_col.label(text="Thresholds:")
        list_row = layers_col.row()
        list_row.template_list("AUTO_REMESHER_UL_layers", "", rprops, "crease_layers", rprops, "crease_layers_index", rows=4)
        list_ops = list_row.column(align=True)
        # list_ops.operator("auto_remesher.threshold_add", icon='ADD', text="")
        # list_ops.operator("auto_remesher.threshold_remove", icon='REMOVE', text="")
        
        ### Crease Visualisation Run Box ###
        run_vis_box = crease_vis_section.box()
        run_vis_box.label(text="Run", icon="PLAY")
        run_visualisation_row = run_vis_box.row()
        run_visualisation_row.operator("auto_remesher.vp_crease_vis", text="Visualise", icon='PLAY')
        run_visualisation_row.operator("auto_remesher.clear_vp_vis", text="Clear", icon='X')