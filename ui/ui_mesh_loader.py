import bpy


class VIEW3D_PT_autoremesher_loader(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Remesher"
    bl_label = "Load Mesh"

    def draw(self, context):
        layout = self.layout
        props = context.scene.auto_remesher
        rprops = props.remesher

        mesh_info_box = layout.box()
        mesh_info_label = mesh_info_box.column(align=True)
        mesh_info_label.label(text="Loaded Mesh Info", icon='OBJECT_DATA')
        mesh_data_row = mesh_info_box.row(align=True)
        mesh_data_row.alignment = 'CENTER'
        if rprops.mesh and getattr(rprops.mesh, "type", None) == 'MESH':
            mesh_data_box = mesh_data_row.box()
            mesh_data_box.label(text=f"Name: {rprops.mesh.name}")
            mesh_data_box.label(text=f"Verts: {len(rprops.mesh.data.vertices)}")
            mesh_data_box.label(text=f"Faces: {len(rprops.mesh.data.polygons)}")
        else:
            mesh_data_row.label(text="No mesh loaded yet.", icon='INFO')
            mesh_data_row.enabled = False

        layout.separator()

        row1 = layout.row(align=True)
        row1.label(text="Select Existing Mesh:")
        row1.template_ID(rprops, "mesh")

        layout.separator()

        row2 = layout.row(align=True)
        row2.label(text="Import New Mesh:")
        row2.operator("auto_remesher.import_mesh", text="Open", icon='FILE_FOLDER')