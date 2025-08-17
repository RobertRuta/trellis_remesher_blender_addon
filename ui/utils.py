import bpy


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