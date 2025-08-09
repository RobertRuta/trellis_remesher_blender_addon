import bpy


class AUTO_REMESHER_OT_gn_crease_visualiser(bpy.types.Operator):
    bl_idname = "auto_remesher.gn_crease_vis"
    bl_label = "Apply GN Crease Visualiser"
    bl_description = "Apply/update a Geometry Nodes modifier that visualizes crease edges"

    def execute(self, context):
        props = context.scene.auto_remesher
        rprops = props.remesher
        obj = rprops.mesh or context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        group = _ensure_crease_gn_group()

        mod_name = "AR_CreaseVis"
        mod = obj.modifiers.get(mod_name)
        if mod is None:
            mod = obj.modifiers.new(mod_name, type='NODES')
        mod.node_group = group

        try:
            for i, socket in enumerate(group.interface.items_tree):
                if getattr(socket, 'in_out', None) != 'INPUT':
                    continue
                if socket.name == 'Viz Threshold':
                    mod[f"Input_{i}"] = rprops.viz_threshold
                elif socket.name == 'Thickness':
                    mod[f"Input_{i}"] = rprops.viz_thickness
        except Exception:
            pass

        try:
            mod["Input_1"] = rprops.viz_threshold if rprops.viz_threshold > 0 else 0.01
            if rprops.viz_thickness <= 0:
                bb = obj.bound_box
                dx = abs(bb[0][0] - bb[6][0])
                dy = abs(bb[0][1] - bb[6][1])
                dz = abs(bb[0][2] - bb[6][2])
                diag = (dx*dx + dy*dy + dz*dz) ** 0.5
                mod["Input_2"] = max(0.005, 0.01 * diag)
            else:
                mod["Input_2"] = rprops.viz_thickness
        except Exception:
            pass

        mod.show_viewport = rprops.show_crease_viz
        mod.show_render = False
        mod.show_in_editmode = True

        return {'FINISHED'}


def _ensure_crease_gn_group():
    name = "AR_CreaseVis"
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    ng = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    ng.is_modifier = True

    in_geo = ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    in_viz_thresh = ng.interface.new_socket(name="Viz Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
    in_viz_thresh.default_value = 0.5
    in_thickness = ng.interface.new_socket(name="Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    in_thickness.default_value = 0.01
    out_geo = ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = ng.nodes
    links = ng.links

    n_in = nodes.new('NodeGroupInput')
    n_out = nodes.new('NodeGroupOutput')

    n_cmp = nodes.new('FunctionNodeCompare')
    n_cmp.data_type = 'FLOAT'
    n_cmp.operation = 'GREATER_EQUAL'

    n_edge_attr_custom = nodes.new('GeometryNodeInputNamedAttribute')
    n_edge_attr_custom.data_type = 'FLOAT'
    n_edge_attr_custom.inputs['Name'].default_value = 'crease_edge'

    n_edge_attr_builtin = nodes.new('GeometryNodeInputNamedAttribute')
    n_edge_attr_builtin.data_type = 'FLOAT'
    n_edge_attr_builtin.inputs['Name'].default_value = 'crease'

    n_max = nodes.new('ShaderNodeMath')
    n_max.operation = 'MAXIMUM'

    n_mesh_to_curve = nodes.new('GeometryNodeMeshToCurve')
    n_curve_to_mesh = nodes.new('GeometryNodeCurveToMesh')
    try:
        n_curve_to_mesh.inputs['Fill Caps'].default_value = True
    except Exception:
        pass
    n_curve_circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    n_curve_circle.mode = 'RADIUS'

    n_join = nodes.new('GeometryNodeJoinGeometry')

    try:
        links.new(n_edge_attr_custom.outputs['Attribute'], n_max.inputs[0])
        links.new(n_edge_attr_builtin.outputs['Attribute'], n_max.inputs[1])
        links.new(n_max.outputs['Value'], n_cmp.inputs['A'])
        links.new(n_in.outputs['Viz Threshold'], n_cmp.inputs['B'])

        links.new(n_in.outputs['Geometry'], n_mesh_to_curve.inputs['Mesh'])
        links.new(n_cmp.outputs['Result'], n_mesh_to_curve.inputs['Selection'])

        links.new(n_curve_circle.outputs['Curve'], n_curve_to_mesh.inputs['Profile Curve'])
        links.new(n_mesh_to_curve.outputs['Curve'], n_curve_to_mesh.inputs['Curve'])
        links.new(n_in.outputs['Thickness'], n_curve_circle.inputs['Radius'])

        links.new(n_in.outputs['Geometry'], n_join.inputs['Geometry'])
        links.new(n_curve_to_mesh.outputs['Mesh'], n_join.inputs['Geometry'])
        links.new(n_join.outputs['Geometry'], n_out.inputs['Geometry'])
    except Exception as e:
        print(f"Error creating GN links: {e}")
        try:
            links.new(n_edge_attr_custom.outputs[0], n_max.inputs[0])
            links.new(n_edge_attr_builtin.outputs[0], n_max.inputs[1])
            links.new(n_max.outputs[0], n_cmp.inputs[0])
            links.new(n_in.outputs[1], n_cmp.inputs[1])
            links.new(n_in.outputs[0], n_mesh_to_curve.inputs[0])
            links.new(n_cmp.outputs[0], n_mesh_to_curve.inputs[1])
            links.new(n_curve_circle.outputs[0], n_curve_to_mesh.inputs[1])
            links.new(n_mesh_to_curve.outputs[0], n_curve_to_mesh.inputs[0])
            links.new(n_in.outputs[2], n_curve_circle.inputs[0])
            links.new(n_in.outputs[0], n_join.inputs[0])
            links.new(n_curve_to_mesh.outputs[0], n_join.inputs[0])
            links.new(n_join.outputs[0], n_out.inputs[0])
        except Exception as e2:
            print(f"Alternative link method also failed: {e2}")

    return ng
