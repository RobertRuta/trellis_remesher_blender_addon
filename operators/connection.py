import bpy


class TRELLIS_OT_check_connection(bpy.types.Operator):
    bl_idname = "trellis.check_connection"
    bl_label = "Check Connection"

    def execute(self, context):
        props = context.scene.auto_remesher

        import requests
        try:
            url = props.server.api_url
            resp = requests.get(f"{url}/status", timeout=2)
            if resp.status_code == 200:
                props.server.connection_status = "✅ Connected"
            else:
                props.server.connection_status = f"⚠ Error {resp.status_code}"
        except Exception as e:
            props.server.connection_status = f"❌ {str(e)}"
        return {'FINISHED'}


