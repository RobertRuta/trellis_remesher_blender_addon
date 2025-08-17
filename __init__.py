import bpy
import inspect

from . import operators, ui, properties

# ---------------- Helpers -----------------
def _get_classes_from_module_ordered(module):
    ordered_names = getattr(module, "__all__", [])
    classes_in_order = []
    if ordered_names:
        for name in ordered_names:
            cls = getattr(module, name, None)
            if inspect.isclass(cls) and cls.__module__ == module.__name__:
                classes_in_order.append(cls)
        return classes_in_order
    
    
def _attach_props_to_context_container(cls):
    target_info = getattr(cls, "__blender_context_target__", None)
    if not isinstance(target_info, tuple) or len(target_info) != 2:
        raise AttributeError(
                f"{cls.__name__} '__blender_context_target__' must be a (context, attr_name) tuple"
            )

    context_type, prop_group_name = target_info
    context_owner = getattr(bpy.types, context_type, None)

    if context_owner is None:
        raise ValueError(f"Invalid Blender context type '{context_type}' for {cls.__name__}")

    # Replace if already present from a previous (failed) registration
    if hasattr(context_owner, prop_group_name):
        try:
            delattr(context_owner, prop_group_name)
        except Exception:
            pass
    setattr(context_owner, prop_group_name, bpy.props.PointerProperty(type=cls))
    _root_properties.append((context_type, prop_group_name))


def _detach_props_from_context_containers():
    for context_type, prop_group_name in _root_properties:
        context_owner = getattr(bpy.types, context_type, None)
        if context_owner and hasattr(context_owner, prop_group_name):
            delattr(context_owner, prop_group_name)
    _root_properties.clear()
    
    
# Store top level property groups and their associated contexts
_root_properties = []


# ---------------- Blender Add-on Setup -----------------
bl_info = {
    "name": "Auto-Remesher",
    "blender": (4, 5, 0),
    "category": "Mesh",
}


# ---------- Blender Add-on Class Registrations ----------
property_classes = _get_classes_from_module_ordered(properties)
operator_classes = _get_classes_from_module_ordered(operators)
ui_classes       = _get_classes_from_module_ordered(ui)

classes_to_register = tuple(property_classes
                            + operator_classes
                            + ui_classes)


def register():
    for cls in classes_to_register:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
            bpy.utils.register_class(cls)

        # If class is not a top level property group, registration is done
        if not issubclass(cls, bpy.types.PropertyGroup)   : continue   # is prop?
        if not hasattr(cls, "__blender_context_target__") : continue   # is top level?
        
        # Otherwise, attach the property group to its blender context target
        _attach_props_to_context_container(cls)

def unregister():
    _detach_props_from_context_containers()

    for cls in reversed(classes_to_register):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass