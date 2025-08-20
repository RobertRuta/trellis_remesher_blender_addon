from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Tuple, List
import numpy as np


@dataclass(frozen=True)
class AttrSpec:
    key: str           # logical key used by our code
    base_name: str     # base name used on the mesh attribute
    domain: str        # 'EDGE' | 'CORNER' | ...
    data_type: str     # 'INT8' | 'BYTE_COLOR' | ...

# Logical keys
K_EDGE_LAYER_ID = "crease_layer_id_mask"
K_CORNER_COLOR_LAYER = "crease_layer_color_corner_mask"
K_CORNER_COLOR_LAYER_EDIT = "crease_layer_color_corner_mask_edit"

EDGE_LAYER_ID_SPEC = AttrSpec(
    key=K_EDGE_LAYER_ID,
    base_name="crease_layer_id",
    domain="EDGE",
    data_type="INT8",
)

CORNER_COLOR_SPEC = AttrSpec(
    key=K_CORNER_COLOR_LAYER,
    base_name="_crease_color",
    domain="CORNER",
    data_type="BYTE_COLOR",
)

CORNER_COLOR_EDIT_SPEC = AttrSpec(
    key=K_CORNER_COLOR_LAYER_EDIT,
    base_name="_crease_color",
    domain="CORNER",
    data_type="BYTE_COLOR",
)

# Track attributes we created so we can clean them up if desired
_CREATED_ATTRIBUTES: List[Tuple[str, str]] = []  # list of (name, domain)


def _get_color_layer_name(spec: AttrSpec, idx: Optional[int], is_edit: bool) -> str:
    if spec.domain != "CORNER":
        return spec.base_name

    if idx is None:
        raise RuntimeError("Layered corner-color attributes require an index (use -1 for 'all').")

    if idx in [-1, -2]:
        prefix = "all" if idx == -1 else "display"
    elif idx >= 0:
        prefix = f"L{idx}"
    suffix = "_edit" if is_edit else ""

    return f"{prefix}{spec.base_name}{suffix}"


def _validate_attr(attr, expect_domain: str, expect_type: str) -> bool:
    # Blender attribute fields: .domain, .data_type
    try:
        return (attr is not None) and (attr.domain == expect_domain) and (attr.data_type == expect_type)
    except Exception:
        return False         
    
    
def get_edge_layer_ids(mesh, *, create: bool = True):
    """
    Ensure/get the EDGE-domain INT8 attribute that stores crease layer ids.
    Returns the Blender attribute.
    """
    spec = EDGE_LAYER_ID_SPEC
    name = spec.base_name
    attr = mesh.attributes.get(name)

    if _validate_attr(attr, spec.domain, spec.data_type):
        return attr

    if not create:
        raise RuntimeError(f"Failed to get '{spec.key}' Blender attribute (expected {spec.domain}/{spec.data_type}).")

    if attr is not None and (attr.domain != spec.domain or attr.data_type != spec.data_type):
        mesh.attributes.remove(attr)
        attr = None

    if attr is None:
        attr = mesh.attributes.new(name=name, type=spec.data_type, domain=spec.domain)
        _CREATED_ATTRIBUTES.append((name, spec.domain))

    return attr
        
        
def set_edge_layer_ids(mesh, data=None, create=True):
    attr = get_edge_layer_ids(mesh, create=create)
    n = len(attr.data)
    if data is None:
        data = np.full(n, -1, dtype=np.int8)
    if n != len(data):
        raise ValueError(f"Data length mismatch. Expected {n} and got {len(data)}")

    attr.data.foreach_set('value', data)
    return attr


def extract_edge_layer_ids(mesh):
    attr = get_edge_layer_ids(mesh, create=False)
    N = len(attr.data)
    data = np.empty(N, dtype=np.int8)
    attr.data.foreach_get('value', data)
    return data


def extract_edge_layer_mask_from_id(mesh, layer_id: int):
    id_map = get_edge_layer_ids(mesh)
    return id_map == layer_id        


def extract_corner_layer_ids(mesh):
    n_corners = len(mesh.loops)
    corner_edge_ids = np.empty(n_corners, dtype=np.int32)
    mesh.loops.foreach_get("edge_index", corner_edge_ids)
    edge_crease_layer_ids = extract_edge_layer_ids(mesh)
    return edge_crease_layer_ids[corner_edge_ids]
        

def extract_corner_layer_mask_for_id(mesh, layer_id: int):
    corner_layer_ids = extract_corner_layer_ids(mesh)
    return corner_layer_ids == layer_id
        

def get_corner_color_layer(mesh, layer_id: int, *, edit: bool=False, create: bool=True):
    spec = CORNER_COLOR_EDIT_SPEC if edit else CORNER_COLOR_SPEC
    name = _get_color_layer_name(spec, layer_id, is_edit=edit)
    attrs = getattr(mesh, "color_attributes", None)
    attr = attrs.get(name) if attrs is not None else mesh.attributes.get(name)

    if _validate_attr(attr, spec.domain, spec.data_type):
        return attr

    if not create:
        raise RuntimeError(f"Failed to get layered corner color '{name}' ({spec.domain}/{spec.data_type}).")

    if attr is not None and (attr.domain != spec.domain or attr.data_type != spec.data_type):
        mesh.attributes.remove(attr)
        attr = None

    if attr is None:
        attr = mesh.attributes.new(name=name, type=spec.data_type, domain=spec.domain)
        _CREATED_ATTRIBUTES.append((name, spec.domain))

    return attr


def set_corner_layer_color(mesh, 
                           layer_id: int, 
                           *, 
                           rgba: Tuple[float, float, float, float]=(1.,1.,1.,1.), 
                           data=None, 
                           edit: bool=False):
    attr = get_corner_color_layer(mesh, layer_id, edit=edit, create=True)
    n = len(attr.data) * 4
    if data is not None:
        if len(data) != n:
            raise ValueError(f"\'data\' has wrong length. Expected {n} got {len(data)}")
        attr.data.foreach_set('color', data)
        return attr
    color = np.array(rgba, dtype=np.float32)
    if color.shape != (4,):
        raise ValueError("rgba must be a 4-tuple of floats in [0, 1].")
    new_color_full = np.repeat(color[None, :], len(attr.data), axis=0).ravel()
    white = np.ones(len(new_color_full), dtype=np.float32)
    mask = extract_corner_layer_mask_for_id(mesh, layer_id)
    mask = np.repeat(mask, 4)
    new_color_data = np.where(mask, new_color_full, white)
    attr.data.foreach_set("color", new_color_data)
    return attr


def extract_corner_color_data(mesh, layer_id: int, *, edit: bool=False, create: bool=False):
    attr = get_corner_color_layer(mesh, layer_id, create=create)
    n = len(attr.data) * 4
    color_data = np.ones(n, dtype=np.float32)
    attr.data.foreach_get('color', color_data)
    layer_mask = color_data < 1
    return layer_mask, color_data


def display_chosen_layer(mesh, layer_id: int):
    attr = get_corner_color_layer(mesh, layer_id, create=False)
    _, data_to_copy = extract_corner_color_data(mesh, layer_id)
    set_corner_layer_color(mesh, layer_id=-2, data=data_to_copy)
    


def delete_created_attributes(mesh, *, domain: Optional[str] = None, data_type: Optional[str] = None, name_pred: Optional[Callable[[str], bool]] = None, ) -> List[str]:
    removed: List[str] = []
    for name, created_domain in list(_CREATED_ATTRIBUTES):
        if domain is not None and created_domain != domain:
            continue

        attr = mesh.attributes.get(name)
        if attr is None:
            _CREATED_ATTRIBUTES.remove((name, created_domain))
            continue

        if domain is not None and attr.domain != domain:
            continue
        if data_type is not None and getattr(attr, "data_type", None) != data_type:
            continue
        if name_pred is not None and not name_pred(name):
            continue

        mesh.attributes.remove(attr)
        removed.append(name)
        _CREATED_ATTRIBUTES.remove((name, created_domain))
        
    return removed


def delete_created_attributes_by_domain(mesh, domain: str) -> List[str]:
    """Remove only created attributes in the given domain."""
    return delete_created_attributes(mesh, domain=domain)


def delete_created_attributes_by_type(mesh, data_type: str) -> List[str]:
    """Remove only created attributes with the given data_type."""
    return delete_created_attributes(mesh, data_type=data_type)



from typing import Callable, List, Optional
import re

# Assumes you have _CREATED_ATTRIBUTES: List[tuple[str, str]]  # (name, domain)
# And (optionally) CORNER_COLOR_SPEC with .base_name, else we'll default:
def _corner_color_base_name() -> str:
    try:
        return CORNER_COLOR_SPEC.base_name  # e.g. "_crease_color"
    except Exception:
        return "_crease_color"

def get_attributes(
    mesh,
    *,
    created_only: bool = False,
    domain: Optional[str] = None,            # 'EDGE' | 'CORNER' | 'POINT' | 'FACE'
    data_type: Optional[str] = None,         # 'INT8' | 'BYTE_COLOR' | 'FLOAT' | ...
    name_pred: Optional[Callable[[str], bool]] = None,
    color_only: bool = False                 # BYTE_COLOR or FLOAT_COLOR
) -> List:
    """
    Generic attribute filter. Returns a list of bpy attribute objects.
    """
    created_names = {name for name, _ in _CREATED_ATTRIBUTES}
    out: List = []
    for attr in mesh.attributes:
        if created_only and attr.name not in created_names:
            continue
        if domain is not None and getattr(attr, "domain", None) != domain:
            continue
        if data_type is not None and getattr(attr, "data_type", None) != data_type:
            continue
        if color_only and getattr(attr, "data_type", None) not in ("BYTE_COLOR", "FLOAT_COLOR"):
            continue
        if name_pred is not None and not name_pred(attr.name):
            continue
        out.append(attr)
    return out

def get_created_attributes(
    mesh,
    *,
    domain: Optional[str] = None,
    data_type: Optional[str] = None,
    name_pred: Optional[Callable[[str], bool]] = None,
    color_only: bool = False
) -> List:
    """Only attributes created by this module (tracked in _CREATED_ATTRIBUTES)."""
    return get_attributes(
        mesh,
        created_only=True,
        domain=domain,
        data_type=data_type,
        name_pred=name_pred,
        color_only=color_only,
    )

def get_attributes_by_domain(mesh, domain: str, *, created_only: bool = False) -> List:
    return get_attributes(mesh, created_only=created_only, domain=domain)

def get_attributes_by_type(mesh, data_type: str, *, created_only: bool = False) -> List:
    return get_attributes(mesh, created_only=created_only, data_type=data_type)

def get_color_attributes(
    mesh,
    *,
    created_only: bool = False,
    include_byte: bool = True,
    include_float: bool = True,
    domain: Optional[str] = None  # usually 'CORNER'
) -> List:
    """Fetch color attributes; optionally constrain to domain or created-only."""
    if include_byte and include_float:
        return get_attributes(mesh, created_only=created_only, domain=domain, color_only=True)
    elif include_byte:
        return get_attributes(mesh, created_only=created_only, domain=domain, data_type="BYTE_COLOR")
    elif include_float:
        return get_attributes(mesh, created_only=created_only, domain=domain, data_type="FLOAT_COLOR")
    else:
        return []

def get_layered_corner_color_attributes(
    mesh,
    *,
    created_only: bool = False,
    include_all_bucket: bool = True,   # include 'all_...' layer
    edit: Optional[bool] = None        # True: only *_edit, False: exclude *_edit, None: both
) -> List:
    """
    Returns CORNER BYTE_COLOR attributes that follow your layered naming:
      L{int}_<base>[_edit], all_<base>[_edit]
    """
    base = _corner_color_base_name()   # e.g. "_crease_color"
    # Build name predicate
    if include_all_bucket:
        # match L\d+_base(_edit)? OR all_base(_edit)?
        pat = re.compile(rf'^(L\d+|all){re.escape(base)}(_edit)?$')
    else:
        # match L\d+_base(_edit)?
        pat = re.compile(rf'^L\d+{re.escape(base)}(_edit)?$')

    def pred(name: str) -> bool:
        m = pat.match(name)
        if not m:
            return False
        has_edit = m.group(2) is not None
        if edit is None:
            return True
        return (edit and has_edit) or ((edit is False) and (not has_edit))

    return get_attributes(
        mesh,
        created_only=created_only,
        domain="CORNER",
        data_type="BYTE_COLOR",
        name_pred=pred,
    )

# Handy debug helper
def summarize_attributes(mesh) -> List[dict]:
    """
    Returns a list of dicts with basic info for quick inspection.
    """
    created_names = {name for name, _ in _CREATED_ATTRIBUTES}
    rows = []
    for attr in mesh.attributes:
        rows.append({
            "name": attr.name,
            "domain": getattr(attr, "domain", None),
            "data_type": getattr(attr, "data_type", None),
            "length": len(attr.data),
            "created_by_us": attr.name in created_names,
        })
    return rows
