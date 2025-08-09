def center_label(layout, text="", icon='NONE'):
    """Draw a center-aligned label inside the given layout."""
    row = layout.row()
    row.alignment = 'CENTER'
    row.label(text=text, icon=icon)
    return row
