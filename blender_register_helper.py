from types import ModuleType
import inspect


# Hoists class into package namespace
def _hoist_class(target_module: ModuleType, cls):
    cls.__module__ = target_module.__name__
    target_module.__dict__[cls.__name__] = cls
    return cls

def collect_and_export_hoist_from_modules(target_module: ModuleType, modules, bpy_types):
    # normalize bpy_types to a tuple of bases
    if isinstance(bpy_types, (list, tuple, set)):
        bpy_types = tuple(bpy_types)
    else:
        bpy_types = (bpy_types,)

    collected = []
    seen = set()  # dedupe classes across submodules by identity

    for mod in modules:
        # iterate only class objects defined in this module namespace
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ != mod.__name__:
                continue

            # must be subclass of any requested bpy base
            if not any(issubclass(cls, base) for base in bpy_types):
                continue

            if cls in seen:
                continue
            seen.add(cls)

            collected.append(_hoist_class(target_module, cls))

    return collected