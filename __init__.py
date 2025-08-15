import bpy
import inspect

from . import operators, ui
from .properties import (
    AutoRemesherServerProperties,
    AutoRemesherGeneratorProperties,
    AutoRemesherThresholdItem,
    AutoRemesherLayerItem,
    AutoRemesherRemesherProperties,
    AutoRemesherProperties,
)


bl_info = {
    "name": "Auto-Remesher",
    "blender": (4, 5, 0),
    "category": "Mesh",
}


def _get_classes_from_module(module):
    return [cls for name, cls in inspect.getmembers(module, inspect.isclass)
            if cls.__module__ == module.__name__]

_property_classes_in_order = (
    AutoRemesherServerProperties,
    AutoRemesherGeneratorProperties,
    AutoRemesherThresholdItem,
    AutoRemesherLayerItem,
    AutoRemesherRemesherProperties,
    AutoRemesherProperties,
)

classes = tuple(_property_classes_in_order
                + tuple(_get_classes_from_module(operators))
                + tuple(_get_classes_from_module(ui)))

_dynamic_properties = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        # Auto-register only root-level properties that declare a context target
        if issubclass(cls, bpy.types.PropertyGroup):
            target_info = getattr(cls, "__blender_context_target__", None)
            if target_info:
                if not isinstance(target_info, tuple) or len(target_info) != 2:
                    raise AttributeError(
                        f"{cls.__name__} '__blender_context_target__' must be a (context, attr_name) tuple"
                    )

                context_type, attr_name = target_info
                context_owner = getattr(bpy.types, context_type, None)

                if context_owner is None:
                    raise ValueError(f"Invalid Blender context type '{context_type}' for {cls.__name__}")

                setattr(context_owner, attr_name, bpy.props.PointerProperty(type=cls))
                _dynamic_properties.append((context_type, attr_name))

def unregister():
    for context_type, attr_name in _dynamic_properties:
        context_owner = getattr(bpy.types, context_type, None)
        if context_owner and hasattr(context_owner, attr_name):
            delattr(context_owner, attr_name)
    _dynamic_properties.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
