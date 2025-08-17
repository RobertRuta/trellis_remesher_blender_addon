from ..blender_register_helper import collect_and_export_hoist_from_modules
import bpy, sys

from . import generation as _generation
from . import import_mesh as _import_mesh
from . import connection as _connection
from . import creases as _creases
from . import vp_visualiser as _vp_vis
from . import thresholds_ui as _thr_ui


_this_module = sys.modules[__name__]
_modules = (_generation, _import_mesh, _connection, _creases, _vp_vis, _thr_ui)

_classes_to_export = collect_and_export_hoist_from_modules(_this_module, 
                                                           _modules, 
                                                           bpy.types.Operator)

__all__ = [cls.__name__ for cls in _classes_to_export]