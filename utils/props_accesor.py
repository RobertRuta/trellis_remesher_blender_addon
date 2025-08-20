from ..properties.thresholds import AutoRemesherLayerItem

def get_props(context):
    return context.scene.auto_remesher

def get_rprops(context):
    return context.scene.auto_remesher.remesher

def get_mesh(context):
    rprops = get_rprops(context)
    mesh_obj = rprops.mesh
    if mesh_obj is None:
        raise ValueError("\'mesh\' property not set.")
    if mesh_obj.type != 'MESH':
        raise ValueError(f"\'mesh\' has wrong type: {mesh_obj.type}. Should be \'MESH\'.")
    return mesh_obj

def get_thresholds(context):
    rprops = get_rprops(context)
    if rprops.is_single_threshold:
        thresholds = [rprops.single_threshold]
    else:
        thresholds = rprops.multi_thresholds
        rprops.sort_thresholds()

    if thresholds is None or len(thresholds) < 1:
        raise ValueError("Failed to get thresholds.")
    
    return thresholds

def get_crease_layers(context):
    rprops = get_rprops(context)
    crease_layers = rprops.crease_layers
    if len(crease_layers) < 1 or crease_layers is None or not all([isinstance(crs, AutoRemesherLayerItem) for crs in crease_layers]):
        raise ValueError("\'crease_layers\' property is not set or broken.")
    
    return crease_layers

def build_crease_layers_from_thresholds(context):
    rprops = get_rprops(context)
    thresholds = get_thresholds(context)
    crease_layers = rprops.crease_layers
    try:
        crease_layers = get_crease_layers(context)
    except ValueError as e:
        crease_layers = rprops.crease_layers
        if len(crease_layers) > 0 and crease_layers is not None:
            raise ValueError(f"Failed to build \'crease_layers\' from \'thresholds\' because \'crease_layers\' is broken.")
    
    for threshold in thresholds:
        rprops.add_crease_layer_from_threshold(threshold)

def update_thresholds_with_creases(context):
    thresholds = get_thresholds(context)
    crease_layers = get_crease_layers(context)
    if len(thresholds) != len(crease_layers):
        raise ValueError("Cannot update \'thresholds\' with \'crease layers\' due to different lengths.")
    
    for i, threshold in enumerate(thresholds):
        threshold.color = crease_layers[i]

def update_creases_with_thresholds(context):
    crease_layers = get_crease_layers(context)
    thresholds = get_thresholds(context)
    if len(thresholds) != len(crease_layers):
        raise ValueError("Cannot update \'crease layers\' with \'thresholds\' due to different lengths.")
    
    for i, crease_layer in enumerate(crease_layers):
        crease_layer.color = thresholds[i].color
        
    
    