import bpy
from .. import utils


class TRELLIS_OT_generate_mesh(bpy.types.Operator):
    bl_idname = "trellis.generate_mesh"
    bl_label = "Generate"
    bl_description = "Run the TRELLIS generator subprocess"

    def execute(self, context):
        props = context.scene.auto_remesher

        props_dict = {
            "text_prompt": props.generator.text_prompt.strip(),
            "image_prompt": props.generator.image_path,
            "generation_quality": props.generator.generation_quality,
        }

        try:
            utils.send_mesh_generation_request_async(
                props_dict, utils.handle_mesh_generation_result
            )
            self.report({'INFO'}, "TRELLIS Generating...")
        except Exception as e:
            self.report({'ERROR'}, f"TRELLIS backend failed to generate mesh: {e}")
            print(e)
        return {'FINISHED'}


