import bpy


class AUTO_REMESHER_UL_thresholds(bpy.types.UIList):
    bl_idname = "AUTO_REMESHER_UL_thresholds"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item is None:
            return
        row = layout.row(align=True)
        row.prop(item, "angle_deg", text="°")
        row.prop(item, "strength", text="S")
        row.prop(item, "color", text="")


class AUTO_REMESHER_OT_threshold_add(bpy.types.Operator):
    bl_idname = "auto_remesher.threshold_add"
    bl_label = "Add Threshold"
    bl_description = "Add a new crease threshold"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        item = rprops.thresholds.add()
        item.uid = rprops.threshold_next_id
        rprops.threshold_next_id += 1
        item.angle_deg = 20.0
        item.strength = 1.0
        item.color = (1.0, 0.0, 0.0, 1.0)
        rprops.thresholds_index = len(rprops.thresholds) - 1
        return {'FINISHED'}


class AUTO_REMESHER_OT_threshold_remove(bpy.types.Operator):
    bl_idname = "auto_remesher.threshold_remove"
    bl_label = "Remove Threshold"
    bl_description = "Remove the selected threshold"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        idx = rprops.thresholds_index
        if 0 <= idx < len(rprops.thresholds):
            rprops.thresholds.remove(idx)
            rprops.thresholds_index = max(0, idx - 1)
        return {'FINISHED'}


class AUTO_REMESHER_OT_threshold_move(bpy.types.Operator):
    bl_idname = "auto_remesher.threshold_move"
    bl_label = "Move Threshold"
    bl_description = "Move the selected threshold up or down"

    direction: bpy.props.EnumProperty(
        items=[('UP', 'Up', ''), ('DOWN', 'Down', '')],
        name="Direction"
    )

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        idx = rprops.thresholds_index
        if self.direction == 'UP' and idx > 0:
            rprops.thresholds.move(idx, idx - 1)
            rprops.thresholds_index = idx - 1
        elif self.direction == 'DOWN' and idx < len(rprops.thresholds) - 1:
            rprops.thresholds.move(idx, idx + 1)
            rprops.thresholds_index = idx + 1
        return {'FINISHED'}


class AUTO_REMESHER_OT_generate_finer_detail(bpy.types.Operator):
    bl_idname = "auto_remesher.generate_finer_detail"
    bl_label = "Show Finer Detail"
    bl_description = "Create two sub-thresholds at 1/2 and 1/4 of the current angle with darker shades, and switch to Multi mode"

    def execute(self, context):
        rprops = context.scene.auto_remesher.remesher
        base_angle = float(rprops.crease_angle_threshold)
        base_strength = float(rprops.crease_strength)
        base_color = rprops.single_threshold_color

        # Switch to multi mode
        try:
            rprops.threshold_mode = 'MULTI'
        except Exception:
            pass

        # Helper to add threshold
        def add_threshold(angle_deg: float, strength: float, color_rgba):
            item = rprops.thresholds.add()
            item.uid = rprops.threshold_next_id
            rprops.threshold_next_id += 1
            item.angle_deg = angle_deg
            item.strength = strength
            item.color = color_rgba

        # Normalize color and create darker shades
        r, g, b, a = float(base_color[0]), float(base_color[1]), float(base_color[2]), float(base_color[3])
        shade1 = (max(0.0, r * 0.5), max(0.0, g * 0.5), max(0.0, b * 0.5), a)
        shade2 = (max(0.0, r * 0.25), max(0.0, g * 0.25), max(0.0, b * 0.25), a)

        # Clear existing thresholds
        rprops.thresholds.clear()

        # Add thresholds in list order: base, half, quarter
        add_threshold(base_angle, base_strength, (r, g, b, a))
        add_threshold(base_angle * 0.5, min(1.0, base_strength), shade1)
        add_threshold(base_angle * 0.25, min(1.0, base_strength), shade2)

        # Select the last added
        rprops.thresholds_index = max(0, len(rprops.thresholds) - 1)

        self.report({'INFO'}, "Generated finer detail thresholds and switched to Multi mode")
        return {'FINISHED'}


