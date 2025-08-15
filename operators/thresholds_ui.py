import random
import bpy
from ..properties.remesher import add_crease_threshold, update_thresholds

# TODO: Need to ensure these are locked to multi mode
class AUTO_REMESHER_UL_thresholds(bpy.types.UIList):
    bl_idname = "AUTO_REMESHER_UL_thresholds"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item is None:
            return
        row = layout.row(align=True)
        layer_id = row.row(align=True)
        layer_id.ui_units_x = 15
        layer_id.label(text=f"L{item.layer_id}")
        angle = row.row(align=True)
        angle.ui_units_x = 20
        angle.prop(item, "angle_deg", text="°")
        row.prop(item, "color", text="")


class AUTO_REMESHER_UL_layers(bpy.types.UIList):
    bl_idname = "AUTO_REMESHER_UL_layers"

    # Optional: nicer spacing across compact rows
    use_filter_show = False

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item:
            return

        # Main row
        row = layout.row(align=True)

        # 1) Layer number (fixed width)
        layer_id = row.row(align=True)
        layer_id.ui_units_x = 0.15
        layer_id.label(text=f"L{item.layer_id}")

        # 2) Eye toggle (always enabled)
        row.prop(
            item, "is_visible",
            text="",
            emboss=True,
            icon=('HIDE_OFF' if item.is_visible else 'HIDE_ON')
        )

        # 3) Everything else is disabled when not visible
        color_box = row.row(align=True)
        color_box.ui_units_x = 0.85
        color_box.prop(item, "color", text="")
        color_box.enabled = item.is_visible


class AUTO_REMESHER_OT_threshold_add(bpy.types.Operator):
    bl_idname = "auto_remesher.threshold_add"
    bl_label = "Add Threshold"
    bl_description = "Add a new crease threshold"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        thresholds = rprops.multi_thresholds
        
        # Add new threshold
        if len(thresholds) > 0:
            new_angle = thresholds[-1].angle_deg / 2
        else:
            new_angle = 20
        random_color = (random.random(), random.random(), random.random(), 1.0)
        threshold = add_crease_threshold(thresholds, new_angle, random_color)
        update_thresholds(thresholds)
        
        # Select the newly added item
        rprops.thresholds_index = threshold.layer_id
        
        self.report({'INFO'}, f"Added threshold at {threshold.layer_id} with angle {threshold.angle_deg}°")
        return {'FINISHED'}


class AUTO_REMESHER_OT_threshold_remove(bpy.types.Operator):
    bl_idname = "auto_remesher.threshold_remove"
    bl_label = "Remove Threshold"
    bl_description = "Remove the selected threshold"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        thresholds = rprops.multi_thresholds
        idx = rprops.thresholds_index
        if 0 <= idx < len(thresholds):
            thresholds.remove(idx)
            rprops.thresholds_index = max(0, idx - 1)
            update_thresholds(thresholds)
        
        return {'FINISHED'}            


class AUTO_REMESHER_OT_generate_finer_detail(bpy.types.Operator):
    bl_idname = "auto_remesher.generate_finer_detail"
    bl_label = "Show Finer Detail"
    bl_description = "Create two sub-thresholds at 1/2 and 1/4 of the current angle with darker shades, and switch to Multi mode"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        base_angle = float(rprops.crease_angle_threshold)
        base_color = rprops.single_threshold_color
        thresholds = rprops.multi_thresholds

        # Switch to multi mode
        rprops.is_single_threshold = False

        # Normalize color and create darker shades
        r, g, b, a = float(base_color[0]), float(base_color[1]), float(base_color[2]), float(base_color[3])
        shade1 = (max(0.0, r * 0.5), max(0.0, g * 0.5), max(0.0, b * 0.5), a)
        shade2 = (max(0.0, r * 0.25), max(0.0, g * 0.25), max(0.0, b * 0.25), a)

        # Clear existing thresholds
        thresholds.clear()

        # Add thresholds in list order: base, half, quarter
        add_crease_threshold(thresholds, base_angle, (r, g, b, a))
        add_crease_threshold(thresholds, base_angle * 0.5, shade1)
        last_added_threshold = add_crease_threshold(thresholds, base_angle * 0.25, shade2)

        # Update layer numbers after generating thresholds
        update_thresholds(thresholds)

        # Select the last added
        rprops.thresholds_index = last_added_threshold.layer_id

        self.report({'INFO'}, "Generated finer detail thresholds and switched to Multi mode")
        return {'FINISHED'}
    
    
class AUTO_REMESHER_OT_set_threshold_mode(bpy.types.Operator):
    bl_idname = "auto_remesher.set_threshold_mode"
    bl_label = "Set Threshold Mode"

    use_single: bpy.props.BoolProperty()

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        rprops.is_single_threshold = self.use_single
        return {'FINISHED'}
