from ..blender_register_helper import collect_and_export_hoist_from_modules
import bpy, sys

from . import server as _server
from . import generator as _generator
from . import thresholds as _thresholds
from . import remesher as _remesher
from . import main as _main


_this_module = sys.modules[__name__]
_modules_to_hoist = (_server, _generator, _thresholds, _remesher, _main)

_classes_to_export = collect_and_export_hoist_from_modules(_this_module, 
                                                           _modules_to_hoist, 
                                                            bpy.types.PropertyGroup)

__all__ = [cls.__name__ for cls in _classes_to_export]
