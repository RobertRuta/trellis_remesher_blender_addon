import random
import bpy


# TODO: Need to ensure these are locked to multi mode
class AUTO_REMESHER_UL_thresholds(bpy.types.UIList):
    bl_idname = "AUTO_REMESHER_UL_thresholds"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item is None:
            return
        row = layout.row(align=True)
        row.prop(item, "angle_deg", text="°")
        row.prop(item, "color", text="")
        row.label(text=f"L{item.layer_number}")


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
        random_colour = (random.random(), random.random(), random.random(), 1.0)
        threshold = add_threshold(thresholds, new_angle, random_colour)
        update_thresholds(thresholds)
        
        # Select the newly added item
        rprops.thresholds_index = threshold.layer_number
        
        self.report({'INFO'}, f"Added threshold at {threshold.layer_number} with angle {threshold.angle_deg}°")
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
        add_threshold(thresholds, base_angle, (r, g, b, a))
        add_threshold(thresholds, base_angle * 0.5, shade1)
        last_added_threshold = add_threshold(thresholds, base_angle * 0.25, shade2)

        # Update layer numbers after generating thresholds
        update_thresholds(thresholds)

        # Select the last added
        rprops.thresholds_index = last_added_threshold.layer_number

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


# Helper to add threshold
def add_threshold(thresholds, angle_deg: float, color_rgba):
    threshold = thresholds.add()
    threshold.angle_deg = angle_deg
    threshold.color = color_rgba
    return threshold

def update_thresholds(thresholds):
    """Reassign layer_number based on descending angle, without touching other values."""
    # Sort actual item references by angle
    sorted_items = sorted(thresholds, key=lambda t: t.angle_deg, reverse=True)

    # Assign new layer numbers
    for new_layer, t in enumerate(sorted_items):
        t.layer_number = new_layer

