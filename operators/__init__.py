import importlib

# Import submodules
from . import generation as _generation
from . import import_mesh as _import_mesh
from . import connection as _connection
from . import creases as _creases
from . import gn_visualiser as _gn_vis
from . import vp_visualiser as _vp_vis

# Hoist classes into this package namespace so the root addon's
# auto-registration (which inspects this module) still works.

EXPORTED_CLASSES = []

def _export_class(cls):
    # Ensure the class appears to be defined in this module for inspector
    try:
        cls.__module__ = __name__
    except Exception:
        pass
    globals()[cls.__name__] = cls
    EXPORTED_CLASSES.append(cls)

# Collect all classes from submodules
for _mod in (_generation, _import_mesh, _connection, _creases, _gn_vis, _vp_vis):
    for _name in dir(_mod):
        _obj = getattr(_mod, _name)
        # Filter bpy operator classes by common Blender base class
        try:
            import bpy
            if isinstance(_obj, type) and issubclass(_obj, bpy.types.Operator):
                _export_class(_obj)
        except Exception:
            continue

__all__ = [cls.__name__ for cls in EXPORTED_CLASSES]