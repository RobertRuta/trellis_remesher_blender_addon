import bpy


class AUTO_REMESHER_OT_import_mesh(bpy.types.Operator):
    bl_idname = "auto_remesher.import_mesh"
    bl_label = "Import Mesh"
    bl_description = "Import a mesh file and set it as the target."

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(
        default="*.obj;*.fbx;*.glb;*.gltf;*.ply;*.stl",
        options={'HIDDEN'}
    )

    def execute(self, context):
        before = set(bpy.data.objects)

        ext = self.filepath.lower()
        if ext.endswith(".obj"):
            self.report({'ERROR'}, "Obj not supported yet")
            return {'CANCELLED'}
        elif ext.endswith(".fbx"):
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        elif ext.endswith(".glb") or ext.endswith(".gltf"):
            bpy.ops.import_scene.gltf(filepath=self.filepath)
        elif ext.endswith(".ply"):
            bpy.ops.import_mesh.ply(filepath=self.filepath)
        elif ext.endswith(".stl"):
            bpy.ops.import_mesh.stl(filepath=self.filepath)
        else:
            self.report({'ERROR'}, "Unsupported file type")
            return {'CANCELLED'}

        after = set(bpy.data.objects)
        new_objects = list(after - before)
        if not new_objects:
            self.report({'ERROR'}, "No mesh imported")
            return {'CANCELLED'}

        new_meshes = [obj for obj in new_objects if obj.type == 'MESH']
        if not new_meshes:
            self.report({'ERROR'}, "No mesh object found in import")
            return {'CANCELLED'}

        imported_obj = new_meshes[-1]

        bpy.ops.object.select_all(action='DESELECT')
        imported_obj.select_set(True)
        context.view_layer.objects.active = imported_obj

        context.scene.auto_remesher.remesher.mesh = imported_obj
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


