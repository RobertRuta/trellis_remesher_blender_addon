from . import ui

bl_info = {
    "name": "Auto-Remesher",
    "blender": (4, 5, 0),
    "category": "Mesh",
}

def register():
    ui.register()
    
def unregister():
    ui.unregister()