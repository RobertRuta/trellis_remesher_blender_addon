from ..generator_backend import TrellisConnector
from .trellis_mesh_to_blender import trellis_mesh_to_blender


def try_generate_mesh(props_dict):
    text_prompt = props_dict["text_prompt"]
    image_prompt = props_dict["image_prompt"]
    
    if len(text_prompt) == 0 and image_prompt is None:
        raise ValueError("No prompt supplied. Please provide a value for \
                        either \'image_prompt\' or \'text_prompt\'.")
    
    # Validate that exactly one prompt type is provided
    if len(text_prompt) > 0 and not image_prompt is None:
        raise ValueError("Both \'text_prompt\' and \'image_prompt\' \
            provided with valid values. Only one allowed.")
    
    # Set final prompt
    if len(text_prompt) > 0:
        prompt = text_prompt
    else:
        prompt = image_prompt
        
    trellis = TrellisConnector()
    
    generated_mesh_output = trellis.send_generate_request(prompt)
    mesh = trellis_mesh_to_blender(generated_mesh_output)
    return mesh